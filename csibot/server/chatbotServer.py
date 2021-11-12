from .server import Server
from .handler import Handler
from ..client import Client
from ..webservices import Query, Ping, Reboot, Model, Running
from ..models import CaseDefault
from ..history import History
from base64 import b64decode
from ..dbconnection import Dbconnection
import dill
import queries

class ChatbotServer(Server):

    def __init__(self, host, port, endpoint, idbot, log):
        """
        :param host: Serving host
        :param port: Serving port
        :param endpoint: Url of DB manager, for get the model
        :param idbot: Id of the bot to start
        """
        super().__init__(host, port, log)
        self.botmanager = Client(endpoint)
        def dbget(key): return self.config.get('DB', key)
        self.dbconnection = Dbconnection(
            schema=dbget('SCHEMA'),
            database=dbget('DATABASE'),
            user=dbget('USER'),
            password=dbget('PASSWORD'),
            dbhost=dbget('DBHOST'),
            dbport=dbget('DBPORT'), 
            log=log)
        self.querysession =  queries.TornadoSession(queries.uri(dbget('DBHOST'), dbget('DBPORT'), dbget('DATABASE'), dbget('USER'), dbget('PASSWORD')))
        
        
        self.history = History('history')
        self.idbot = idbot
        self.id_instance = 0
        self.model = None
        self.load()

        # Add handler
        services = {s.name: s(self) for s in [
            Query,
            Ping,
            Reboot
        ]}
        self.add_handler(Handler, services=services)

    def load(self):
        """
        Load chatbot from manager with idbot.
        If idbot=0, load base bot
        """
        if self.idbot > 0:
            # Get model and create class
            body = Model.Body(idbot=self.idbot)
            response = self.botmanager.post('model', **body)
            if response.error.code == 0:
                data = Model.Result(response.result).data
                self.model = dill.loads(b64decode(data))
            else:
                raise Exception(response.error.description)

            # Inform botmanager
            response = self.botmanager.post('running', port=self.port, idbot=self.idbot)
            if response.error.code == 0:
                self.id_instance = Running.Result(response.result).idinstance
            else:
                self.log.warning(f"Failed to inform botmanager that I'm running: {response.error.description}")

        else:
            self.model = CaseDefault()
            self.log.warning("I'm running an empty chatbot")
