import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options
from IClockAccessHandles import CdataHandler, GetrequestHandler, DeviceCmdHandler, UserServer
from MongoDbApi import initialize_database
from LocalTrace import init_local_trace

define("port", default=8002, help="run on the given port", type=int)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    initialize_database()
    init_local_trace()

    app = tornado.web.Application(
        handlers=[
            (r"/iclock/cdata?(.*)", CdataHandler),
            (r"/iclock/getrequest?(.*)", GetrequestHandler),
            (r"/iclock/devicecmd?(.*)", DeviceCmdHandler),
            (r"/UserServer/user?(.*)", UserServer)
        ]
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
