from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import ServiceError
from ..client import Client
from .ping import Ping
from datetime import datetime


class Monitor(Service):

    name = 'monitor'

    class Body(ApiObject):
        pass

    class Result(ApiObject):
        instances = Attribute(typ=list, required=True)

    async def serve(self, body):
        instances = self._read('sql_read_instances', None).to_dict('records')
        self._commit()
        # Ping all instances
        for instance in instances:
            endpoint = f"http://{instance['host']}:{instance['port']}"
            if instance['status'] == 1:
                chatbot = Client(endpoint)
                body = Ping.Body()
                response = chatbot.post('ping', **body)
                if response.error.code == 0:
                    idinstance = Ping.Result(response.result).idinstance
                    if idinstance == instance['id']:
                        continue
                    else:
                        self.log.warning(f"Instance at {endpoint} changed")
                else:
                    if not response.error.code == 404:
                        self.log.error(response.error.code)
                self._update('sql_update_instance', instance['id'])
        self._commit()

        # Read new data
        instances = self._read('sql_read_active_instances', None).to_dict('records')

        self._commit()
        self._close()

        # Replace timestamps with strings
        for instance in instances:
            for key, value in instance.items():
                if isinstance(value, datetime):
                    instance[key] = str(value)

        return dict(
            instances=instances
        )
