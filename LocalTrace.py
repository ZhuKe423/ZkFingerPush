# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler
import os.path
import time

LTrace = logging.getLogger("tornado.access")
'''
LTraceDebug = None
LTraceInfo = None
LTraceWarn = None
LTraceError = None
'''
LTraceDebug = LTrace.debug
LTraceInfo = LTrace.info
LTraceWarn = LTrace.warning
LTraceError = LTrace.error


def init_local_trace():
    global LTrace
    LTrace.setLevel(logging.DEBUG)
    log_path = os.getcwd() + '/Logs/'
    log_name = log_path + 'zkpush.log'
    logfile = log_name
    # each file size is 20M, max files is 10
    fh = RotatingFileHandler(logfile, maxBytes=20*1024*1024, backupCount=10)
    fh.setLevel(logging.INFO)  # 输出到file的log等级的开关
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    LTrace.addHandler(fh)
    '''
    console = logging.StreamHandler()
    console.setLevel(logging.FATAL)
    console.setFormatter(formatter)
    LTrace.addHandler(console)
    '''
    global LTraceDebug
    global LTraceInfo
    global LTraceWarn
    global LTraceError
    LTraceDebug = LTrace.debug
    LTraceInfo = LTrace.info
    LTraceWarn = LTrace.warning
    LTraceError = LTrace.error
    logging.getLogger("tornado.access").propagate = False
    LTraceInfo('init_local_trace is done!!')


if __name__ == "__main__":
    init_local_trace()
    a = {'udbg': 23432, 'words': 'hello everything'}
    LTraceInfo('test a = {0}'.format(a))
    LTraceInfo(a)

