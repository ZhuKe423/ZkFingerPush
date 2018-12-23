# -*- coding: utf-8 -*-

SystemSettings = {
    'CloudServerUrl': {
        'updateStudent': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/updateStudent',
        'syncAttLog': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/syncRecord',
        'newRecord': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/newRecord',
        'getStudent': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/getStudent',
        'getCommand': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/getCommand',
        'sendErrorLogs': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/sendErrorLogs',
        'updateClockInfo': 'http://www.jzk12.com/wx4/w18/WeiXiao/StudentAttendance/updateClockInfo'
    },
    'GeneralSetting': {
        'raspyNumSerialNum': 'Haha-1',
        'clientToken': 'gh_221e39c94190',
        'syncStudentInterval': 1 * 60 * 60,  # 1 hour
        'syncAttLogTime': 23 * 60 * 60,      # 23:00:00
        'maxDevLosTime': 12 * 60 * 60,       # 12 hours
        'getServerCmdInterval': 3 * 60      # 10 min
    }
}