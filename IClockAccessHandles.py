
from tornado.web import RequestHandler
from IClockInterface import IClockInterfaceList


def dispatch_commands(command, content=None):
    # print(command)
    feedbacks = []
    for (k, v) in command.items():
        if k in IClockInterfaceList:
            # print(type(IClockInterfaceList[k]).__name__)
            if type(IClockInterfaceList[k]).__name__ == 'dict':
                if v in IClockInterfaceList[k]:
                    feedbacks += IClockInterfaceList[k][v](command['SN'], command, content)
            else:
                feedbacks += IClockInterfaceList[k](command['SN'], command, content)

    return feedbacks


class CdataHandler(RequestHandler):

    def get(self, input):
        print('CdataHandler get in')
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        if 'SN' not in command:
            print('This Clock Accessing without SN number!!!')
            return
        cmdlines = dispatch_commands(command)
        # print('CdataHandler get cmdlines:' + str(cmdlines))
        for cmdline in cmdlines:
            self.write(cmdline)
        print('CdataHandler get out')

    def post(self, post):
        """
        :param post: This parameter is always none
        :return:
        """
        print('CdataHandler post in')
        content = str(self.request.body, encoding="gbk")
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        if 'SN' not in command:
            print('This Clock Accessing without SN number!!!')
            return
        cmdlines = dispatch_commands(command, content)
        # print('CdataHandler post cmdlines:' + str(cmdlines))
        for cmdline in cmdlines:
            self.write(cmdline)
        print('CdataHandler post out')


class GetrequestHandler(RequestHandler):
    def get(self, input):
        """
        :param input: this parameter always None
        :return:
        """
        print('GetrequestHandler get in')
        # content = str(self.request.body, encoding="gbk")
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        # print('GetrequestHandler command:', str(command))
        if 'SN' not in command:
            print('This Clock Accessing without SN number!!!')
            return
        if len(command) == 1:
            command['HeartBeat'] = 'Clock Heart Beat'
        # print('GetrequestHandler get content', content)
        cmdlines = dispatch_commands(command)

        for cmdline in cmdlines:
            print('GetrequestHandler get cmdline:', cmdline)
            self.write(cmdline)
        print('GetrequestHandler get out')


class DeviceCmdHandler(RequestHandler):
    def post(self, post):
        """
        :param post: This parameter is always none
        :return:
        """
        print('DeviceCmdHandler post in')
        content = str(self.request.body, encoding="gbk")
        args = self.request.arguments
        command = {}
        for a in args:
            command[a] = self.get_argument(a)
        if 'SN' not in command:
            print('This Clock Accessing without SN number!!!')
            return
        if len(command) == 1:
            command['CmdResp'] = 'Clock Command Response'
        cmdlines = dispatch_commands(command, content)
        # print('DeviceCmdHandler post cmdlines:' + str(cmdlines))
        for cmdline in cmdlines:
            self.write(cmdline)
        print('DeviceCmdHandler post out')
