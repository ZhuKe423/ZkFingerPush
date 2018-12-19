# -*- coding: utf-8 -*-
import time
import ServerAccessApi as ServerApi
import IClockCmdGenerator as ClockCmdGenerator
import MongoDbApi as db
from config import SystemSettings
from MongoDbApi import info_log, warning_log

ServerProcessor = {}


class ServerCmdProcessor:

    def __init__(self, clock_sn):
        self.sn = clock_sn
        self.cmd_id = 0
        self.last_update_students = 0
        self.last_tick = 0
        self.updating_users = False

    def is_updating_users(self):
        return self.updating_users

    def parse_one_user(self, user):
        is_need_update = False
        old_user = db.get_student(self.sn, user['PIN'])
        if old_user is None:
            is_need_update = True
        else:
            if user['fingers'] is not None:
                for finger in user['fingers']:
                    old_finger = db.get_student_finger(self.sn, user['PIN'], finger['FID'], finger['Size'])
                    if old_finger is None:
                        is_need_update = True
            # print('parse_student_data check finger: ', is_need_update)
            if user['Card'] is not None:
                if old_user['Card'] != user['Card'] and not is_need_update:
                    is_need_update = True
        # print(user['Name'] + ':' + user['PIN'] + ' is_need_update ', is_need_update)
        if is_need_update:
            db.update_student(self.sn, user)
            # print(user['Name']+':'+user['PIN']+' has been updated!!')
            ClockCmdGenerator.update_user_info(self.sn, user)
            if user['fingers'] is not None:
                for finger in user['fingers']:
                    finger['PIN'] = user['PIN']
                    # print('update user finger:' + user['PIN'] + ',' + 'FID=' + str(finger['FID']) + 'Size:' + str(finger['Size']))
                    ClockCmdGenerator.update_fp_info(self.sn, finger)

    def parse_student_data(self, response):
        # print(response)
        self.last_update_students = response['timeStamp']
        page = int(response['page'])
        total_pages = int(int(response['count'])/20) + (1 if (int(response['count']) % 20) else 0)

        if response['users'] is not None:
            for user in response['users']:
                self.parse_one_user(user)
        info_log(self.sn, '获取服务器端最新用户数据('+response['count']+')，第'+response['page']+'页已完成！')
        if page < total_pages:
            page += 1
            ServerApi.get_all_students(self.sn, page, self.last_update_students, self.parse_student_data)
        else:
            self.updating_users = False

    def get_students(self, options):
        self.updating_users = True
        if db.get_students_number(self.sn) > int(3100):  # 考勤机最大的指纹用户数量为3200
            db.remove_all_students(self.sn)
            warning_log(self.sn, '考勤机用户数量>3100, max is 3200, 清除树莓派上的用户数据，重新下载用户数据！！')
        ServerApi.get_all_students(self.sn, 1, self.last_update_students, self.parse_student_data)

    def send_error_logs_response(self, response):
        # info_log(self.sn, '上传ErrorLog，完成！')
        pass

    def send_error_logs(self, options):
        logs_obj = db.get_all_error_logs(self.sn)
        logs = []
        for log in logs_obj:
            log['sn'] = self.sn
            logs.append(log)
            ServerApi.send_error_log(self.sn, [log], self.send_error_logs_response)
        if len(logs) > 0:
            # ServerApi.send_error_log(self.sn, logs, self.send_error_logs_response)
            db.del_all_error_logs(self.sn)
        logs = []
        logs_obj = db.get_all_error_logs(SystemSettings['GeneralSetting']['raspyNumSerialNum'])
        for log in logs_obj:
            log['sn'] = SystemSettings['GeneralSetting']['raspyNumSerialNum']
            logs.append(log)
            ServerApi.send_error_log(SystemSettings['GeneralSetting']['raspyNumSerialNum'], [log], None)
        if len(logs) > 0:
            # ServerApi.send_error_log(SystemSettings['GeneralSetting']['raspyNumSerialNum'], logs, None)
            db.del_all_error_logs(SystemSettings['GeneralSetting']['raspyNumSerialNum'])

    def let_clock_sync_log(self, options):
        # print('let_clock_sync_log option len:', len(options))
        if options == '':
            start = time.strftime("%Y-%m-%d 00:00:01", time.localtime())
            end = time.strftime("%Y-%m-%d 23:59:59", time.localtime())
            ClockCmdGenerator.query_history_logs(self.sn, start, end)
        elif len(options) == 37:
            time_items = options.split(',')
            # print('let_clock_sync_log:', time_items)
            ClockCmdGenerator.query_history_logs(self.sn, time_items[0], time_items[1])

    def clear_all_users(self, options):
        db.del_all_cmd_lines(self.sn)
        db.remove_all_students(self.sn)
        ClockCmdGenerator.clear_all_data(self.sn)
        self.get_error_logs(None)
        warning_log(self.sn, '清除所有数据！！')

    def send_clock_info_response(self, response):
        # print('send_clock_info_response in:', response)
        info_log(self.sn, '上传考勤机信息，完成！')

    def send_clock_info(self, options):
        # print('web send_clock_info in')
        clock_info = {
            'info': db.get_clock_info(self.sn),
            'heartbeat': db.get_heartbeat_setting(self.sn)
        }
        ServerApi.update_clock_info(self.sn, clock_info, self.send_clock_info_response)

    def update_one_user(self, user_info):
        # print(user_info)
        pass


    def parse_server_cmd(self, response):
        """
        :param response:
                {
                    'timeStamp':  123344455,
                    'SN': 'XXXXXXXXXXXXXX'  #设备SN 号
                    'cmd_list' : {
                        'getErrLog': '',
                        'updatestd' : '',
                        'syncAttLog': '',
                        'clearAll'  : '',
                        'getDeviceInfo' : '',
                        'updateone': dict
                        .....
                    }
                }
        :return:
        """
        cmd_dispatch = {
            'getErrLog': self.send_error_logs,
            'updatestd': self.get_students,
            'syncAttLog': self.let_clock_sync_log,
            'clearAll': self.clear_all_users,
            'getDeviceInfo': self.send_clock_info,
            'updateone': self.update_one_user,
        }
        # print('parse_server_cmd in:', response)
        if 'cmd_list' in response:
            cmd = response['cmd_list']
            if len(cmd) > 0:
                for (k, v) in cmd.items():
                    if k in cmd_dispatch:
                        cmd_dispatch[k](v)
                    else:
                        warning_log(self.sn, '服务器下发错误的命令：'+k+str(v))

    def get_server_cmd(self):
        ServerApi.get_server_cmd(self.sn, self.parse_server_cmd)

    def send_att_log_response(self, response):
        # print("send_att_log_response in:", response)
        pass

    def send_att_log(self, record):
        ServerApi.send_new_record(self.sn, record, self.send_att_log_response)


def server_processor(clock_sn):
    if clock_sn in ServerProcessor:
        return ServerProcessor[clock_sn]
    else:
        ServerProcessor[clock_sn] = ServerCmdProcessor(clock_sn)
        return ServerProcessor[clock_sn]
