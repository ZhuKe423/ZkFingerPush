# -*- coding: utf-8 -*-
import time
import random
from config import SystemSettings
from IClockCmdProcessor import clock_cmd_processor
from ServerCmdProcessor import server_processor
import IClockCmdGenerator as CmdGenerator
import MongoDbApi as db
from MongoDbApi import info_log, warning_log

CMD_IS_SUCCESS = 0
CMD_IS_SEND = 100
CMD_IS_NEW = 9999
TheHandlerOfClocks = {}
DefaultClockOptions = {
        'Stamp'         : '82983982',
        'OpStamp'       : '9238883',
        'PhotoStamp'    : '9238833',
        'ErrorDelay'    : '60',
        'Delay'         : '10',
        'TransTimes'    : '00:00;14:05',
        'TransInterval' : '1',
        'TransFlag'     : '1111000000',
        'Realtime'      : '1',
        'Encrypt'       : '0',
        'ServerVer'     : '3.4.1 2010 - 06 - 07',
        'ATTLOGStamp'   : '82983982',
        'OPERLOGStamp'  : '82983982'
}

DefaultHeartBeatSetting = {
    'maxDevLosTime'         : SystemSettings['GeneralSetting']['maxDevLosTime'],
    'syncStudentInterval'   : SystemSettings['GeneralSetting']['syncStudentInterval'],
    'syncAttLogTime'        : SystemSettings['GeneralSetting']['syncAttLogTime'],
    'getServerCmdInterval'  : SystemSettings['GeneralSetting']['getServerCmdInterval'],
    'lastSyncUser'          : 82983982,
    'lastKick'              : 82983982,
    'lastServerCmd'         : 82983982,
    'lastSyncLog'           : 82983982,
    'sendInfoInterval'      : 30 * 60,
    'lastSendInfo'          : 82983982
}


class IClockHandle:
    def __init__(self, clock_sn):
        self.sn = clock_sn
        self.cmd_processor = clock_cmd_processor(clock_sn)
        self.server_processor = server_processor(clock_sn)
        self.options = db.get_clock_options(clock_sn)
        if self.options is None:
            self.options = DefaultClockOptions
            db.update_clock_options(clock_sn, DefaultClockOptions)
        self.heart_beat = db.get_heartbeat_setting(clock_sn)
        if self.heart_beat is None:
            self.heart_beat = DefaultHeartBeatSetting
            self.heart_beat[''] += random.randrange(0, 600, 30)
            db.update_heartbeat_setting(clock_sn, DefaultHeartBeatSetting)
        info_log(self.sn, '考勤机('+self.sn+')上线！！')
        CmdGenerator.clock_info(self.sn)

    def get_options(self):
        return self.options

    def check_server_cmd(self, kick_time):
        if (kick_time - self.heart_beat['lastServerCmd']) > self.heart_beat['getServerCmdInterval']:
            print('check_server_cmd !')
            self.server_processor.get_server_cmd()
            self.heart_beat['lastServerCmd'] = kick_time

    def check_send_clock_info(self, kick_time):
        if (kick_time - self.heart_beat['lastSendInfo']) > self.heart_beat['sendInfoInterval']:
            self.server_processor.send_clock_info(None)
            self.heart_beat['lastSendInfo'] = kick_time

    def check_sync_log(self, kick_time):
        sync_time = kick_time - kick_time % 86400 + time.timezone + self.heart_beat['syncAttLogTime']
        if (kick_time > sync_time) and (self.heart_beat['lastSyncLog'] < sync_time):
            print('check_sync_log !')
            self.heart_beat['lastSyncLog'] = kick_time
            CmdGenerator.new_logs(self.sn)
            info_log(self.sn, '考勤机(' + self.sn + ') do check_sync_log()！！')
            self.server_processor.send_error_logs(self.sn, None)

    def check_clock_los(self, kick_time):
        if (kick_time - self.heart_beat['lastKick']) > self.heart_beat['maxDevLosTime']:
            print('check_clock_los !')
            CmdGenerator.new_logs(self.sn)
            self.server_processor.get_students(None)
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.heart_beat['lastKick']))
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            CmdGenerator.query_history_logs(self.sn, start_time, end_time)
            self.heart_beat['lastSyncLog'] = kick_time
            self.heart_beat['lastSyncUser'] = kick_time
            info_log(self.sn, '考勤机(' + self.sn + ') 恢复连接！！check_clock_los()')

    def check_update_students(self, kick_time):
        if (kick_time - self.heart_beat['lastSyncUser']) > self.heart_beat['syncStudentInterval']:
            print('check_update_students !')
            self.server_processor.get_students(None)
            self.heart_beat['lastSyncUser'] = kick_time
            info_log(self.sn, '考勤机(' + self.sn + ') 定时同步用户数据！！check_update_students()')

    def kick_ass(self):
        kick_time = int(time.time())
        self.sync_clock_users()
        self.check_clock_los(kick_time)
        self.check_server_cmd(kick_time)
        self.check_sync_log(kick_time)
        self.check_update_students(kick_time)
        self.heart_beat['lastKick'] = kick_time
        db.update_heartbeat_setting(self.sn, self.heart_beat)
        self.check_send_clock_info(kick_time)

    def sync_clock_users(self):
        info = db.get_clock_info(self.sn)
        if info is None:
            return
        student_num = db.get_students_number(self.sn)

        if int(info['UserCount']) != student_num:
            if db.get_new_cmd_lines(self.sn).count() > 0:
                return

            if int(info['UserCount']) != 0:
                CmdGenerator.clear_all_data(self.sn)
                info['UserCount'] = 0
                db.update_clock_info(self.sn, info)
                warning_log(self.sn, '考勤机(' + self.sn + ')用户数量与树莓派用户数量不一致,清除考勤机数据！！')
            else:
                users = db.get_students(self.sn)
                for user in users:
                    CmdGenerator.update_user_info(self.sn, user)
                    if user['fingers'] is not None:
                        for finger in user['fingers']:
                            finger['PIN'] = user['PIN']
                            CmdGenerator.update_fp_info(self.sn, finger)
                    warning_log(self.sn, '考勤机(' + self.sn + ')用户数量与树莓派用户数量不一致,重新同步！！')


def clock_handle(clock_sn, is_create=True):
    if clock_sn in TheHandlerOfClocks:
        return TheHandlerOfClocks[clock_sn]
    elif is_create:
        TheHandlerOfClocks[clock_sn] = IClockHandle(clock_sn)
        return TheHandlerOfClocks[clock_sn]
    else:
        return None


