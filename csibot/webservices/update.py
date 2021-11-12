from .service import Service
from ..client import Client
from .insert import Insert
from ..protocol import ApiObject, Attribute
from .exceptions import InstanceIsDownError


class Update(Service):

    name = 'update'

    class Body(ApiObject):
        data = Attribute(typ=Insert.Body, required=True)
        host = Attribute(typ=str, required=True)
        port = Attribute(typ=int, required=True)

    class Result(ApiObject):
        idbot = Attribute(typ=int, required=True)

    async def serve(self, body):
        # Create client
        endpoint = f"http://{body.host}:{body.port}"
        chatbot = Client(endpoint)

        # Ping chatbot
        response = chatbot.post('ping')
        if response.error.code > 0:
            raise InstanceIsDownError(endpoint)

        # Insert
        insert = Insert(self.server)
        result = insert(body.data, self.request)

        # Reboot
        response = chatbot.post('reboot', idbot=result.idbot)
        if response.error.code > 0:
            raise InstanceIsDownError(endpoint)

        return dict(idbot=result.idbot)
