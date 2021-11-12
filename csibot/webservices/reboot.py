from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import ServiceError


class Reboot(Service):

    name = 'reboot'

    class Body(ApiObject):
        idbot = Attribute(typ=int, required=True)

    class Result(ApiObject):
        success = Attribute(typ=bool, required=True)

    async def serve(self, body):
        self.server.idbot = body.idbot
        return dict(success=True)

    def close(self):
        self.server.load()
