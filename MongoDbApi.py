# -*- coding: utf-8 -*-
import time
from pymongo import MongoClient
from functools import wraps
from config import SystemSettings
from LocalTrace import LTraceDebug

MongoDBClient = None
zkpush_db = None
"""
the Max DB size is 1.2G 
MongoDB colletions and fields define:
    ClockInfo: sn, ~DeviceName, MAC, TransactionCount ...
    ClockOptions: sn, Stamp, OpStamp, PhotoStamp, ErrorDelay, Delay ...
    ClockErrorLog: type(0:Info, 1:Warning, 2: Error),time,sn,content
    ClockCmdLine: sn, cmdId, state, cmdLine 
    HeartBeatSetting: sn, last_time, sync_time ...
    StudentInfo: sn, PIN, NAME, CARD,fingers=[{TMP, FID, SIZE},...]
    ServerCmdLine: sn, cmdId, state, cmd
"""


def initialize_database():
    global MongoDBClient
    global zkpush_db
    MongoDBClient = MongoClient('localhost', 27017)
    zkpush_db = MongoDBClient['zkfpush']
    info_log(SystemSettings['GeneralSetting']['raspyNumSerialNum'],
             '树莓派('+SystemSettings['GeneralSetting']['raspyNumSerialNum']+')开机！！')


def mongodb_update_one(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        if handle['collection'] in zkpush_db.collection_names(include_system_collections=False):
            this_query = handle['query']
            new_value = {'$set': handle['value']}
            return zkpush_db[handle['collection']].update(this_query, new_value, True, False)
        else:
            zkpush_db[handle['collection']].insert_one(handle['value'])
    return decorated


def mongodb_insert_one(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        return zkpush_db[handle['collection']].insert_one(handle['value'])
    return decorated


def mongodb_insert_many(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        zkpush_db[handle['collection']].insert_many(handle['value'])
    return decorated


def mongodb_find_one(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        if handle['collection'] in zkpush_db.collection_names(include_system_collections=False):
            this_query = handle['query']
            if 'fields' in handle:
                data = zkpush_db[handle['collection']].find_one(this_query, handle['fields'])
            else:
                data = zkpush_db[handle['collection']].find_one(this_query, {'_id': 0, 'sn': 0})
            return data
        else:
            return None
    return decorated


def mongodb_find(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        if handle['collection'] in zkpush_db.collection_names(include_system_collections=False):
            this_query = handle['query']
            obj = zkpush_db[handle['collection']].find(this_query, {'_id': 0, 'sn': 0})
            if 'sort' in handle:
                obj = obj.sort(handle['sort']['key'], handle['sort']['value'])
            if 'limit' in handle:
                obj = obj.limit(int(handle['limit']))
            return obj
        else:
            return None
    return decorated


def mongodb_del_one(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        if handle['collection'] in zkpush_db.collection_names(include_system_collections=False):
            this_query = handle['query']
            return zkpush_db[handle['collection']].delete_one(this_query)
        else:
            return None
    return decorated


def mongodb_del(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        handle = func(*args, **kwargs)
        if handle['collection'] in zkpush_db.collection_names(include_system_collections=False):
            this_query = handle['query']
            return zkpush_db[handle['collection']].delete_many(this_query)
        else:
            return None
    return decorated


@mongodb_update_one
def update_clock_info(clock_sn, info):
    """
    :param clock_sn: 考勤机编号
    :param info: 考勤机基础信息
    :return:
    """
    info['sn'] = clock_sn
    handle = {
        'collection': 'ClockInfo',
        'query': {'sn': clock_sn},
        'value': info
    }
    return handle


@mongodb_find_one
def get_clock_info(clock_sn):
    """
    :param clock_sn: 考勤机编号
    :return:
    """
    handle = {
        'collection': 'ClockInfo',
        'query': {'sn': clock_sn},
        'fields': {'_id': 0}
    }
    return handle


@mongodb_update_one
def update_clock_options(clock_sn, options):
    """
    :param clock_sn: 考勤机编号
    :param options:  考勤机配置信息
    :return:
    """
    options['sn'] = clock_sn
    handle = {
        'collection': 'ClockOptions',
        'query': {'sn': clock_sn},
        'value': options
    }
    return handle


@mongodb_find_one
def get_clock_options(clock_sn):
    """
    :param clock_sn: 考勤机编号
    :return:
    """
    handle = {
        'collection': 'ClockOptions',
        'query': {'sn': clock_sn},
    }
    return handle


@mongodb_insert_one
def add_error_log(clock_sn, log):
    """
    :param clock_sn: 考勤机编号
    :param log: {'type': Error/Warning/Info, 'function': xxxxx, 'content': 'xxxxxxx', 'timestamp': xxxxxxx}
    :return:
    """
    log['sn'] = clock_sn
    handle = {
        'collection': 'ClockErrorLog',
        'value': log
    }
    return handle


def info_log(clock_sn, content):
    # type(0:Info, 1:Warning, 2: Error),time,sn,content
    log = {
        'type': 0,
        'time': int(time.time()),
        'content': content
    }
    add_error_log(clock_sn, log)


def warning_log(clock_sn, content):
    # type(0:Info, 1:Warning, 2: Error),time,sn,content
    log = {
        'type': 1,
        'time': int(time.time()),
        'content': content
    }
    add_error_log(clock_sn, log)


def error_log(clock_sn, content):
    # type(0:Info, 1:Warning, 2: Error),time,sn,content
    log = {
        'type': 2,
        'time': int(time.time()),
        'content': content
    }
    add_error_log(clock_sn, log)


@mongodb_find
def get_all_error_logs(clock_sn):
    handle = {
        'collection': 'ClockErrorLog',
        'query': {'sn': clock_sn},
    }
    return handle


@mongodb_del
def del_all_error_logs(clock_sn):
    handle = {
        'collection': 'ClockErrorLog',
        'query': {'sn': clock_sn},
    }
    return handle


@mongodb_update_one
def update_heartbeat_setting(clock_sn, setting):
    setting['sn'] = clock_sn
    handle = {
        'collection': 'HeartBeatSetting',
        'query': {'sn': clock_sn},
        'value': setting
    }
    return handle


@mongodb_find_one
def get_heartbeat_setting(clock_sn):
    handle = {
        'collection': 'HeartBeatSetting',
        'query': {'sn': clock_sn},
    }
    return handle


@mongodb_insert_many
def add_new_students(students):
    """
    :param students: [{'sn': 考勤机编号，’PIN':xxxxxx,....},...]
    :return:
    """
    handle = {
        'collection': 'StudentInfo',
        'value': students
    }
    return handle


@mongodb_update_one
def update_student(clock_sn, user):
    handle = {
        'collection': 'StudentInfo',
        'query': {'sn': clock_sn, 'PIN': user['PIN']},
        'value': user
    }
    return handle


def get_students_number(clock_sn):
    return zkpush_db['StudentInfo'].find({'sn': clock_sn}).count()


@mongodb_find_one
def get_student(clock_sn, pin):
    """
    :param clock_sn: 考勤机编号
    :param pin: 学生学号/工号
    :return:
    """
    handle = {
        'collection': 'StudentInfo',
        'query': {'sn': clock_sn, 'PIN': pin}
    }
    return handle


@mongodb_find
def get_students(clock_sn):
    handle = {
        'collection': 'StudentInfo',
        'query': {'sn': clock_sn}
    }
    return handle


@mongodb_find_one
def get_student_finger(clock_sn, pin, fid, size):
    handle = {
        'collection': 'StudentInfo',
        'query': {'sn': clock_sn, 'PIN': pin, 'fingers': {'$elemMatch': {'FID': fid, 'Size': size}}}
    }
    return handle


@mongodb_del
def remove_all_students(clock_sn):
    handle = {
        'collection': 'StudentInfo',
        'query': {'sn': clock_sn}
    }
    return handle


@mongodb_insert_one
def add_cmd_line(clock_sn, cmd_id, cmd_line):
    # ClockCmdLine: sn, cmdId, state(0:成功,100:已发送，9999:新加), cmdLine
    LTraceDebug('db: {0}'.format(cmd_line[0:80]))
    handle = {
        'collection': 'ClockCmdLine',
        'value': {'sn': clock_sn, 'cmdId': cmd_id, 'state': 9999, 'cmdLine': cmd_line}
    }
    return handle


@mongodb_update_one
def update_cmd_line(clock_sn, cmd_data):
    handle = {
        'collection': 'ClockCmdLine',
        'query': {'sn': clock_sn, 'cmdId': cmd_data['cmdId']},
        'value': cmd_data
    }
    return handle


@mongodb_find
def get_new_cmd_lines(clock_sn, limit=20):
    handle = {
        'collection': 'ClockCmdLine',
        'query': {'sn': clock_sn, 'state': 9999},
        'fields': {'_id': 0},
        'sort': {'key': 'cmdId', 'value': 1},
        'limit': limit
    }
    return handle

@mongodb_find
def get_all_cmd_lines(clock_sn, limit=20):
    handle = {
        'collection': 'ClockCmdLine',
        'query': {'sn': clock_sn},
        'fields': {'_id': 0},
        'sort': {'key': 'cmdId', 'value': 1},
        'limit': limit
    }
    return handle

@mongodb_find_one
def get_cmd_line(clock_sn, cmd_id):
    handle = {
        'collection': 'ClockCmdLine',
        'query': {'sn': clock_sn, 'cmdId': cmd_id},
        'fields': {'_id': 0},
    }
    return handle


@mongodb_del_one
def del_cmd_line(clock_sn, cmd_id):
    handle = {
        'collection': 'ClockCmdLine',
        'query': {'sn': clock_sn, 'cmdId': cmd_id}
    }
    return handle


@mongodb_del
def del_all_cmd_lines(clock_sn):
    handle = {
        'collection': 'ClockCmdLine',
        'query': {'sn': clock_sn}
    }
    return handle


@mongodb_insert_one
def add_one_server_cmd(clock_sn, cmd_id, cmd):
    handle = {
        'collection': 'ServerCmdLine',
        'value': {'sn': clock_sn, 'cmdId': cmd_id, 'state': 9999, 'cmdLine': cmd}
    }
    return handle


if __name__ == "__main__":
    sn = 'A3MA183160364'
