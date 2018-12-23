# -*- coding: utf-8 -*-
from functools import wraps
from IClockCmdProcessor import clock_cmd_processor
from IClockHandle import clock_handle
from ServerCmdProcessor import server_processor
import IClockCmdGenerator as CmdGenerator
from LocalTrace import LTraceDebug


def debug_decorate(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print(func.__name__+' in')
        result = func(*args, **kwargs)
        print(func.__name__ + ' out')
        return result
    return decorated


def get_option_all(clock_sn, command, content=None):
    cmd_lines = CmdGenerator.options_all(clock_sn, clock_handle(clock_sn).get_options())
    return cmd_lines


def parse_operate_table_parameters(content):
    """
    :param content:
            USER PIN=982 Name=Richard Passwd=9822 Card=[09E4812202] Grp=1 TZ=...
            FP PIN=982 FID=1 Valid=1 TMP=ocoRgZPRN8EwJNQxQTY......
            OPLOG 0\t0\t2018-12-07 15:25:17\t0\t0\t0\t0\nOPLOG 4\t0\t2018-12-07 15:36:55\t0\t0\t0\t0\\n
    :return:
    """
    def get_oplog_data(log_content):
        op_log = log_content.split('\t')
        return op_log

    def get_user_data(user_content):
        user_items = user_content.split('\t')
        user_item_data = {}
        for user_item_data in user_items:
            if item != '':
                tmp = user_item_data.split('=')
                item_data[tmp[0]] = tmp[1]
        return user_item_data
    op_types = {
        # 目前只支持这几种type
        'OPLOG': get_oplog_data,
        'USER': get_user_data,
        'FP': get_user_data
    }

    items = content.split('\n')
    data = []
    for item in items:
        break_index = item.find(' ')
        op_type = item[0:break_index]
        content = item[break_index+1:]
        if op_type in op_types:
            item_data = {
                'OpType': op_type,
                'data': op_types[op_type](content)
            }
            data.append(item_data)

    return data


def add_clock_operate_log(clock_sn, command, content=None):
    if content is None:
        return None
    operations = parse_operate_table_parameters(content)
    # print('add_clock_operate_log operation:', operations)
    feedback = ['OK']
    return feedback


def parse_attendance_table_parameters(content):
    """
    :param content:
            982 2008-02-25 12:08:21 1 0
            PIN——用户的考勤号码
            TIME——考勤时间
            STATUS——考勤状态（参见表2-3）
            VERIFY——验证方式（参见表2-3）
            WORKCODE——工作代码
            RESERVED1——保留1
            RESERVED2——保留2
    :return:
    """
    if content is None:
        return None
    items = content.split('\n')
    data = []
    for item in items:
        if item != '':
            item_data = item.split('\t')
            data.append({
                'PIN': item_data[0],
                'TIME': item_data[1],
                'STATUS': int(item_data[2]),
                'VERIFY': item_data[3],
                'WORKCODE': item_data[4],
                'RESERVED1': item_data[5],
                'RESERVED2': item_data[6],
            })
    return data


def add_clock_attendance_log(clock_sn, command, content=None):
    if content is None:
        return None
    records = parse_attendance_table_parameters(content)
    for record in records:
        server_processor(clock_sn).send_att_log(record)
    LTraceDebug(records)
    return ['OK']


def update_clock_information(clock_sn, command, content=None):
    """
    :param clock_sn:
    :param command:
    :param content: INFO=Ver6.39 Apr 28 2008,2,0,0,192.168.1.201,10,7,15,11,011
                    INFO=固件版本号,登记用户数,登记指纹数,考勤记录数,考勤机IP 地址，指纹算法版本
    :return:
    """
    LTraceDebug("update_clock_information "+clock_sn)
    tmp = command['INFO'].split(',')
    info = {
        'FWVersion': tmp[0],
        'UserCount': tmp[1],
        'FPCount': tmp[2],
        'TransactionCount': tmp[3],
        'IPAddress': tmp[4],
        'FPVersion': tmp[5]
    }
    LTraceDebug('update_clock_information info: {0}'.format(info))
    clock_cmd_processor(clock_sn).update_clock_basic_info(info)
    return []


def cmd_info_response(clock_sn, command, content):
    LTraceDebug('cmd_info_response ' + str(command))
    return []


def cmd_check_response(clock_sn, command, content):
    LTraceDebug('cmd_check_response ' + str(command))
    return []


def heart_beat_process(clock_sn, command, content):
    LTraceDebug('heart_beat_process ' + str(command))
    clock_handle(clock_sn).kick_ass()
    cmd_line = clock_cmd_processor(clock_sn).cmd_lines_need_to_send()
    if cmd_line is None:
        return []
    else:
        return cmd_line


def parse_cmd_return_data(content):
    """
    :param content:
            ID=0001&Return=0&CMD=INFO   # first line the command which I sent
            ~DeviceName=S30             # the follow lines are the returned data
            MAC=00:17:61:12:8b:78
            TransactionCount=15
            ....
    :return:
    """
    def get_command(cmd_content):
        cmd_items = cmd_content.split('&')
        LTraceDebug(cmd_items)
        cmd_data = {}
        for cmd_item in cmd_items:
            if cmd_item != '':
                tmp = cmd_item.split('=')
                cmd_data[tmp[0]] = tmp[1]
        return cmd_data

    def get_command_data(data_items):
        data = {}
        for item in data_items:
            if item != '':
                tmp = item.split('=')
                # LTraceDebug('get_command_data tmp:'+str(tmp))
                data[tmp[0]] = tmp[1]
        return data
    if content is None:
        return None
    items = content.split('\n')
    command = get_command(items[0])
    if command['CMD'] == 'INFO':
        if len(items) > 1:
            command['data'] = get_command_data(items[1:])
        else:
            command['data'] = None
        return command
    else:
        commands = [command]
        if len(items) > 1:
            for item in items[1:]:
                tmp = get_command(item)
                if len(tmp) > 0:
                    commands.append(tmp)
        return commands


def cmd_return_response(clock_sn, command, content):
    LTraceDebug('cmd_return_response ' + str(command))
    LTraceDebug('cmd_return_response content:' + content)
    cmd_response = parse_cmd_return_data(content)
    LTraceDebug(str(cmd_response))
    if type(cmd_response).__name__ != 'list':
        clock_cmd_processor(clock_sn).cmd_return_dispatch(cmd_response)
    else:
        for it_cmd in cmd_response:
            clock_cmd_processor(clock_sn).cmd_return_dispatch(it_cmd)
    return ['OK']


IClockInterfaceList = {
    'options': {'all': get_option_all},
    'table': {
                'OPERLOG': add_clock_operate_log,
                'ATTLOG': add_clock_attendance_log
             },
    'INFO': update_clock_information,
    'CMD': {
                'INFO': cmd_info_response,
                'CHECK': cmd_check_response
            },
    'HeartBeat': heart_beat_process,
    'CmdResp': cmd_return_response
}
