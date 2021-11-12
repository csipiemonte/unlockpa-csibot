from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import ServiceError
from datetime import datetime


class Running(Service):

    name = 'running'

    class Body(ApiObject):
        port = Attribute(typ=int, required=True)
        idbot = Attribute(typ=int, required=True)
        description = Attribute(typ=str, required=False, default='')

    class Result(ApiObject):
        idinstance = Attribute(typ=int, required=True)

    async def serve(self, body):
        ts = datetime.now()
        data = [dict(
            description=body.description,
            host=self.request.remote_ip,
            port=body.port,
            status=1,
            ts_creation=ts,
            id_bot=body.idbot
        )]
        id_instance = self._insert('sql_insert_instance', data, return_id=True)
        self._commit()
        self._close()
        return dict(idinstance=id_instance)
