# -*- coding: utf-8 -*-
import MongoDbApi as db
from MongoDbApi import error_log
import  threading
CMD_IS_SUCCESS = 0
CMD_IS_SEND = 100
CMD_IS_NEW = 9999
ClockCmdProcessor = {}


class IClockCmdProcessor:
    def __init__(self, clock_sn):
        self.sn = clock_sn
        self.cmdId = 0
        self.cmdId_lock = threading.Lock()

    def inc_cmd_id(self):
        if self.cmdId_lock.acquire():
            self.cmdId += 1
            self.cmdId_lock.release()
        return self.cmdId

    def update_clock_basic_info(self, info):
        # print('update_clock_basic_info in:', info)
        db.update_clock_info(self.sn, info)
        return

    def cmd_lines_need_to_send(self):
        obj = db.get_new_cmd_lines(self.sn)
        cmd_lines = []
        for cmd_line in obj:
            cmd_lines.append(cmd_line['cmdLine'])
            cmd_line['state'] = CMD_IS_SEND
            db.update_cmd_line(self.sn, cmd_line)
        return cmd_lines

    def cmd_return_dispatch(self, response):
        dispatch_table = {
            'INFO': self.update_clock_basic_info,
            # 'DATA':
        }
        # print('cmd_return_dispatch in', response)
        if response['CMD'] in dispatch_table:
            dispatch_table[response['CMD']](response['data'])
        if int(response['Return']) != 0:
            cmd = db.get_cmd_line(self.sn, int(response['ID']))
            if cmd is not None:
                error_log(self.sn, 'failed ('+response['Return']+'):'+cmd['cmdLine'][0:80])
        db.del_cmd_line(self.sn, int(response['ID']))


def clock_cmd_processor(clock_sn):
    if clock_sn in ClockCmdProcessor:
        return ClockCmdProcessor[clock_sn]
    else:
        ClockCmdProcessor[clock_sn] = IClockCmdProcessor(clock_sn)
        return ClockCmdProcessor[clock_sn]

