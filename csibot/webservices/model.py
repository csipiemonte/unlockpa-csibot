from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import PickleNotFoundError, ModelBadRequestError
from os import path
from base64 import b64encode


class Model(Service):

    name = 'model'

    class Body(ApiObject):
        idbot = Attribute(typ=int, required=True)

    class Result(ApiObject):
        data = Attribute(typ=str, required=True)

    async def serve(self, body):

        # Check file
        dillfile = self._dillfile(self.server.dillpath, body.idbot)
        if not path.isfile(dillfile):
            raise PickleNotFoundError(dillfile)

        # Create model
        with open(dillfile, mode='rb') as fp:
            data = b64encode(fp.read()).decode()

        return dict(
            data=data
        )
