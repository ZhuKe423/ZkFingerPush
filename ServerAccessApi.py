# -*- coding: utf-8 -*-
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
import urllib
import json
from config import SystemSettings
from functools import wraps

AccessUrl = SystemSettings['CloudServerUrl']
_TOKEN = SystemSettings['GeneralSetting']['clientToken']
http_client = AsyncHTTPClient()


def post_response_callback(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        post_data = urllib.parse.urlencode(handle['data']).encode('utf-8')
        request = HTTPRequest(url=handle['url'], method='POST', body=post_data, follow_redirects=False,
                              connect_timeout=200, request_timeout=600)
        print(func.__name__ + ":url->", handle['url'])

        def response_handle(response):
            if response.error:
                print(func.__name__+":error->", response.error)
            else:
                # print(response.body)
                decode_data = json.loads(response.body.decode('utf-8'))
                if handle['callback'] is not None:
                        handle['callback'](decode_data)
                        print(handle['callback'].__name__ + ":success！！")
        http_client.fetch(request, response_handle)
    return decorated


@post_response_callback
def get_all_students(clock_sn, page=1, last_time=0, callback=None):
    """
    从服务获取最新的学生数据
    """
    data = {'token': _TOKEN, 'SN': clock_sn, 'page': page, 'timeStamp': last_time}
    handle = {
        'url': AccessUrl['updateStudent'],
        'callback': callback,
        'data': data
    }
    return handle


@post_response_callback
def send_new_record(clock_sn, record, callback):
    """
    发送新的考勤记录
    :param clock_sn: 考勤机编号
    :param record: record = {'PIN':xxxxxxxx, 'TIME':xxxxxx}
    :param callback: response callback function
    :return:
    """
    data = {'token': _TOKEN, 'SN': clock_sn, 'record': json.dumps(record)}
    handle = {
        'url': AccessUrl['newRecord'],
        'callback': callback,
        'data': data
    }
    return handle


@post_response_callback
def sync_attendance_log(clock_sn, records, callback):
    """
    :param records: [{'PIN':xxxxxxxx, 'TIME':xxxxxx},...]
    :param clock_sn: 考勤机编号
    :param callback: response callback function
    :return:
    """
    data = {'token': _TOKEN, 'SN': clock_sn, 'records': json.dumps(records)}
    handle = {
        'url': AccessUrl['SyncAttLog'],
        'callback': callback,
        'data': data
    }
    return handle


@post_response_callback
def get_server_cmd(clock_sn, callback):
    """
    :param clock_sn: 考勤机编号
    :param callback: response callback function
    :return:
    """
    data = {'token': _TOKEN, 'SN': clock_sn}
    handle = {
        'url': AccessUrl['getCommand'],
        'callback': callback,
        'data': data
    }
    return handle


@post_response_callback
def send_error_log(clock_sn, logs, callback):
    """
    :param clock_sn: 考勤机编号
    :param logs: error logs
    :param callback: response callback function
    :return:
    """
    data = {'token': _TOKEN, 'SN': clock_sn, 'logs': json.dumps(logs)}
    handle = {
        'url': AccessUrl['sendErrorLogs'],
        'callback': callback,
        'data': data
    }
    return handle


@post_response_callback
def update_clock_info(clock_sn, info, callback):
    """
    :param clock_sn: 考勤机编号
    :param info: {'info':{...},'hearbeat':{xxxxx}}
    :param callback: response callback function
    :return:
    """
    data = {'token': _TOKEN, 'SN': clock_sn, 'info': json.dumps(info)}
    handle = {
        'url': AccessUrl['updateClockInfo'],
        'callback': callback,
        'data': data
    }
    return handle


if __name__ == "__main__":
    import tornado.options
    import MongoDbApi as db
    tornado.options.parse_command_line()
    db.initialize_database()
    sn = 'A3MA183160364'
    test_record = {'PIN': '181001', 'TIME': '2018-12-1 13:31:00'}

    def response_print(response):
        print(response)

    def response_new_record(response):
        print('response_new_record:')
        print(response)

    def send_clock_info(clock_sn):
        print('web send_clock_info in')
        clock_info = {
            'info': db.get_clock_info(clock_sn),
            'heartbeat': db.get_heartbeat_setting(clock_sn)
        }
        update_clock_info(clock_sn, clock_info, None)

    def send_error_logs(clock_sn):
        logs_obj = db.get_all_error_logs(clock_sn)
        logs = []
        for log in logs_obj:
            log['sn'] = clock_sn
            logs.append(log)
            send_error_log(clock_sn, [log], None)
        logs_obj = db.get_all_error_logs(SystemSettings['GeneralSetting']['raspyNumSerialNum'])
        for log in logs_obj:
            log['sn'] = SystemSettings['GeneralSetting']['raspyNumSerialNum']
            logs.append(log)
            send_error_log(SystemSettings['GeneralSetting']['raspyNumSerialNum'], [log], None)

    def parse_server_cmd(response):
        print('parse_server_cmd in:', response)

    # get_server_cmd(sn, parse_server_cmd)
    send_error_logs(sn)
    # send_clock_info(sn)
    # get_all_students(sn, 0, 1, response_print)
    # send_new_record(sn, test_record, response_new_record)
    IOLoop.instance().start()

