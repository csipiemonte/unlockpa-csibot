from .server import Server
from .handler import Handler
from ..dbconnection import Dbconnection
from ..webservices import Model, Train, Insert, Remove, Running, Monitor, Update
import os


class BotmanagerServer(Server):

    def __init__(self, host, port, log):
        """
        :param host: Serving host
        :param port: Serving port
        """
        super().__init__(host, port, log)

        # Create attributes
        def dbget(key): return self.config.get('DB', key)
        self.dbconnection = Dbconnection(
            schema=dbget('SCHEMA'),
            database=dbget('DATABASE'),
            user=dbget('USER'),
            password=dbget('PASSWORD'),
            dbhost=dbget('DBHOST'),
            dbport=dbget('DBPORT'), log=log)
        self.dillpath = self.config.get('COMMON', 'DILLPATH')
        os.makedirs(self.dillpath, exist_ok=True)

        # Add handler
        services = {s.name: s(self) for s in [
            Model,
            Train,
            Insert,
            Remove,
            Running,
            Monitor,
            Update
        ]}
        self.add_handler(Handler, services=services)
