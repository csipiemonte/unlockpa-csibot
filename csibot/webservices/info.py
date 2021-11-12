from tornado.web import RequestHandler
from datetime import datetime


class Info(RequestHandler):

    path = '/info'

    async def get(self):
        now = datetime.now()
        response = {
            'version': '0.2.0',
            'timestamp': int(datetime.timestamp(now)),
            'datetime': now.strftime('%Y-%m-%d %H:%M')
        }
        self.write(response)
