from ..protocol import ApiRequest, ApiResponse, ApiError
from ..webservices.exceptions import ServiceError, ServiceNoError, ServiceNotFoundError
from tornado.web import RequestHandler, HTTPError
from tornado import gen
import json
import os


class Handler(RequestHandler):

    path = '/'

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request)
        self.services = kwargs.setdefault('services', {})
        self.server = kwargs['server']
        self.log = self.server.log
    
    
    async def get(self, *args, **kwargs):
        for i in range(5):
            print(i)
            await gen.sleep(1)

    async def post(self, *args, **kwargs):
        """
        Do POST method
        """
        # Create object from request
        try:
            api_request = ApiRequest(json.loads(self.request.body.decode()))
            debug_string = api_request.tojson()
            debug_string = debug_string if len(debug_string) < 512 else f'[{len(debug_string)} bytes]'
            self.log.debug(debug_string)
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            self.server.log.warning(str(e))
            raise HTTPError(400, str(e))

        # Parse request
        idreq = api_request.id
        body = api_request.body
        service =  self.services.get(api_request.service)

        # Execute service
        try:
            if service:
                result = await service(body, self.request)
                self.send_response(idreq, result)
                service.close()
            else:
                raise ServiceNotFoundError(api_request.service)
        except ServiceError as e:
            self.send_response(idreq, err=e)

    def send_response(self, idreq, result=None, err=None):
        """
        Return result applying protocol
        :param idreq: id request (int)
        :param result: body of response (dict)
        :param err: instance of ServiceError class (ServiceError)
        """
        apiResponse = ApiResponse(
            id=idreq,
            result=result or {},
            error=err.dict if err else ServiceNoError().dict
        )
        self.write(apiResponse)
        self.finish()

    def write_error(self, status_code, **kwargs):
        """
        Write info on error occurred on output.
        Usually it's HTTPError with status_code >= 400
        """
        if 'exc_info' in kwargs.keys() and status_code < 500:
            typ, value, tb = kwargs['exc_info']
            self.write(ApiError(
                code=status_code,
                description=str(value)
            ))
            self.finish()
        else:
            super().write_error(status_code, **kwargs)

    def log_exception(self, typ, value, tb):
        """
        When occurred HTTPError, log the message
        :param typ: type of Exception
        :param value: instance of Exception
        :param tb: traceback
        """
        if typ is HTTPError and value.status_code < 500:
            self.server.log.warning(value)
        else:
            fname = os.path.split(tb.tb_frame.f_code.co_filename)[1]
            self.server.log.error(f"{value} - {fname} [{tb.tb_lineno}]")
