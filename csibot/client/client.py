from ..protocol import ApiRequest, ApiResponse, ApiError
from urllib.parse import urljoin
import requests
import json


class Client:

    def __init__(self, endpoint, path='/'):
        self.endpoint = endpoint
        self.path = path
        self._idreq = 0

    def get_new_id(self):
        """
        Increment id request
        :return: id request (int)
        """
        self._idreq += 1
        return self._idreq

    def post(self, service, timeout=100, **kwargs):
        """
        Send body by protocol to endpoint/service
        :param service: name of service (str)
        :param timeout: timeout of post request (int)
        :param kwargs: data body for service (dict)
        :return: response from server
        """
        idreq = self.get_new_id()
        api_request = ApiRequest(
            id=idreq,
            service=service,
            body=kwargs
        )
        try:
            resp = requests.post(urljoin(self.endpoint, self.path), json=api_request, timeout=timeout)
            api_resp = ApiResponse(json.loads(resp.content.decode()))
        except requests.exceptions.ConnectionError:
            return self.return_error(idreq, f"Client can't establish connection with service {service}", code=404)
        except json.JSONDecodeError:
            return self.return_error(idreq, f"Invalid response from service {service}")
        if api_resp.id != api_request.id:
            return self.return_error(idreq, "Id request not valid")
        return api_resp

    @staticmethod
    def return_error(idreq, description, code=500):
        return ApiResponse(
            id=idreq,
            result={},
            error=ApiError(
                code=code,
                description=description
            )
        )
