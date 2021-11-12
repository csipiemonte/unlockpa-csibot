from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import ServiceError
from datetime import datetime


class Ping(Service):

    name = 'ping'

    Body = ApiObject

    class Result(ApiObject):
        idinstance = Attribute(typ=int, required=True)

    async def serve(self, body):
        return dict(
            idinstance=self.server.id_instance
        )
