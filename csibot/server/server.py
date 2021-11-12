from ..config import config, configSql
import tornado.ioloop
import tornado.web
import logging


class Server:

    def __init__(self, host, port, log):
        """
        :param host: Serving host
        :param port: Serving port
        :param log: logger object
        """
        self.host = host
        self.port = port
        self.log = log
        self._handlers = []
        self.config = config
        self.queries = configSql
        self.app = None
        self.history = None

    def add_handler(self, cls, **kwargs):
        """
        Add a new handler to Application
        :param cls: Class of handler to add
        :param kwargs: Arguments to pass to __init__ method
        """
        kwargs['server'] = self
        self._handlers.append((cls.path, cls, kwargs))

    def run(self):
        """
        Create and run httpServer
        """
        self.app = tornado.web.Application(self._handlers, log_function=self.log.httpLogger,serve_traceback=True)
        self.app.listen(self.port, address=self.host)
        self.log.info(f'Start listening on {self.host}:{self.port}')
        tornado.ioloop.IOLoop.instance().start()
