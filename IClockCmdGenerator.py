# -*- coding: utf-8 -*-
from functools import wraps
import MongoDbApi as db
from IClockCmdProcessor import clock_cmd_processor

CMD_UPDATE_DEV_USER = 'DATA UPDATE USERINFO'
CMD_UPDATE_DEV_USERFINGER = 'DATA UPDATE FINGERTMP'
CMD_DEL_DEV_USER = 'DATA DELETE USERINFO'
CMD_QUERY_DEV_USER = "DATA QUERY USERINFO"
CMD_QUERY_DEV_ATTLOG = 'DATA QUERY ATTLOG'
CMD_DEV_INFO = 'INFO'
CMD_DEV_CHECK = 'CHECK'
CMD_CLEAR_DEV_ATTLOG = 'CLEAR LOG'
CMD_CLEAR_DEV_ALL = 'CLEAR DATA'
CMD_SET_DEV_OPTION = 'SET OPTION'
CMD_GET_NEW_LOG = 'LOG'


def options_all(clock_sn, options):
    """
    this a iclock/cdata command, not need to wait for the iclock/request
    :param clock_sn: 考勤机编号
    :param options: {'Stamp':xxx,'OpStamp':xxxx,.....}
    :return:
    """
    cmd_lines = ['GET OPTION FROM: ' + clock_sn + '\n']
    for (k, v) in options.items():
        cmd_lines.append(format("%s=%s\n" % (k, v)))
    return cmd_lines


def clock_info(clock_sn):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    db.add_cmd_line(clock_sn, cmd_id, format("C:%04d:%s\n" % (cmd_id, CMD_DEV_INFO)))


def check_news(clock_sn):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    db.add_cmd_line(clock_sn, cmd_id, format("C:%04d:%s\n" % (cmd_id, CMD_DEV_CHECK)))


def clear_att_log(clock_sn):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    db.add_cmd_line(clock_sn, cmd_id, format("C:%04d:%s\n" % (cmd_id, CMD_CLEAR_DEV_ATTLOG)))


def new_logs(clock_sn):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    db.add_cmd_line(clock_sn, cmd_id, format("C:%04d:%s\n" % (cmd_id, CMD_GET_NEW_LOG)))


def clear_all_data(clock_sn):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    db.add_cmd_line(clock_sn, cmd_id, format("C:%04d:%s\n" % (cmd_id, CMD_CLEAR_DEV_ALL)))


def update_user_info(clock_sn, info):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    cmd_line = format("C:%04d:%s PIN=%s\tName=%s\tPri=%s\tCard=%s\n" %
                      (cmd_id, CMD_UPDATE_DEV_USER, str(info['PIN']), info['Name'], info['Pri'],
                       info['Card'])).encode('gbk', 'ignore')
    db.add_cmd_line(clock_sn, cmd_id, cmd_line)


def update_fp_info(clock_sn, info):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    cmd_line = format("C:%04d:%s PIN=%s\tFID=%d\tSize=%s\tValid=%d\tTMP=%s\n" %
                      (cmd_id, CMD_UPDATE_DEV_USERFINGER, str(info['PIN']), info['FID'], info['Size'],
                       info['Valid'], info['TMP']))
    db.add_cmd_line(clock_sn, cmd_id, cmd_line)


def query_history_logs(clock_sn, start, end):
    cmd_id = clock_cmd_processor(clock_sn).inc_cmd_id()
    db.add_cmd_line(clock_sn, cmd_id,
                    format("C:%04d:%s StartTime=%s\tEndTime=%s\n" % (cmd_id, CMD_QUERY_DEV_ATTLOG, start, end)))


if __name__ == "__main__":
    class ClockCommandGenerator:
        def __init__(self, clock_sn):
            self.sn = clock_sn
            self.cmdIds = 0

        def test_commands(self):
            self.cmdIds += 1
            cmd_lines = [
                '',
                format("C:%04d:%s\n" % (self.cmdIds, CMD_DEV_INFO)),
                format("C:%04d:%s\n" % (self.cmdIds+1, CMD_DEV_CHECK)),
                format("C:%04d:%s\n" % (self.cmdIds+2, CMD_CLEAR_DEV_ATTLOG)),
                format("C:%04d:%s\n" % (self.cmdIds+3, CMD_GET_NEW_LOG)),
                ]
            if self.cmdIds >= len(cmd_lines):
                return None
            self.cmdIds = 5
            # cmd_line = cmd_lines[self.cmdIds]
            return cmd_lines


    ClockCmdHandle = ClockCommandGenerator('A3MA183160364')
