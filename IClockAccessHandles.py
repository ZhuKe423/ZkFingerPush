
from tornado.web import RequestHandler
from IClockInterface import IClockInterfaceList
from LocalTrace import LTraceDebug, LTraceWarn


def dispatch_commands(command, content=None):
    LTraceDebug(command)
    feedbacks = []
    for (k, v) in command.items():
        if k in IClockInterfaceList:
            LTraceDebug(type(IClockInterfaceList[k]).__name__)
            if type(IClockInterfaceList[k]).__name__ == 'dict':
                if v in IClockInterfaceList[k]:
                    feedbacks += IClockInterfaceList[k][v](command['SN'], command, content)
            else:
                feedbacks += IClockInterfaceList[k](command['SN'], command, content)

    return feedbacks


class CdataHandler(RequestHandler):

    def get(self, input):
        LTraceDebug('CdataHandler get in')
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        if 'SN' not in command:
            LTraceWarn('This Clock Accessing without SN number!!!')
            return
        cmdlines = dispatch_commands(command)
        for cmdline in cmdlines:
            self.write(cmdline)
            LTraceDebug('CdataHandler CmdLine: {0}'.format(cmdline[0:80]))
        LTraceDebug('CdataHandler get out')

    def post(self, post):
        """
        :param post: This parameter is always none
        :return:
        """
        LTraceDebug('CdataHandler post in')
        content = str(self.request.body, encoding="gbk")
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        if 'SN' not in command:
            LTraceWarn('This Clock Accessing without SN number!!!')
            return
        cmdlines = dispatch_commands(command, content)
        for cmdline in cmdlines:
            self.write(cmdline)
            LTraceDebug('CdataHandlerPost CmdLine: {0}'.format(cmdline[0:80]))
        LTraceDebug('CdataHandler post out')


class GetrequestHandler(RequestHandler):
    def get(self, input):
        """
        :param input: this parameter always None
        :return:
        """
        LTraceDebug('GetrequestHandler get in')
        # content = str(self.request.body, encoding="gbk")
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        LTraceDebug('GetrequestHandler command:'+str(command))
        if 'SN' not in command:
            LTraceWarn('This Clock Accessing without SN number!!!')
            return
        if len(command) == 1:
            command['HeartBeat'] = 'Clock Heart Beat'
        cmdlines = dispatch_commands(command)

        for cmdline in cmdlines:
            LTraceDebug('send cmdline: {0}'.format(cmdline[0:80]))
            self.write(cmdline)
        LTraceDebug('GetrequestHandler get out')


class DeviceCmdHandler(RequestHandler):
    def post(self, post):
        """
        :param post: This parameter is always none
        :return:
        """
        LTraceDebug('DeviceCmdHandler post in')
        content = str(self.request.body, encoding="gbk")
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        if 'SN' not in command:
            LTraceWarn('This Clock Accessing without SN number!!!')
            return
        if len(command) == 1:
            command['CmdResp'] = 'Clock Command Response'
        cmdlines = dispatch_commands(command, content)
        for cmdline in cmdlines:
            self.write(cmdline)
        LTraceDebug('DeviceCmdHandler post out')
