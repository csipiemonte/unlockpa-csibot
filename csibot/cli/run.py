from .command import Command
from ..server import ChatbotServer


class Run(Command):
    """Run a new instance of chatbot"""

    name = 'run'
    arguments = [
        dict(name='--host', type=str, default='localhost', help='Serving host'),
        dict(name='--port', type=int, default=5001, help='Serving port'),
        dict(name='--endpoint', type=str, default='http://localhost:5401', help='Botmanager endpoint'),
        dict(name='--idbot', type=int, default=0, help='Bot id')
    ]

    def main(self, args):
        self.log.info(f'Started with arguments: {args}')
        chatbot = ChatbotServer(args.host, args.port, args.endpoint, args.idbot, self.log)
        chatbot.run()
