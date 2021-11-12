from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import ServiceError


class Remove(Service):

    name = 'remove'

    class Body(ApiObject):
        idbot = Attribute(typ=int, required=True)

    class Result(ApiObject):
        success = Attribute(typ=bool, required=True)

    async def serve(self, body):
        self._delete('sql_delete_bot', body.idbot)
        self._commit()
        self._close()
        return dict(success=True)
