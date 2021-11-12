from .command import Command
from ..server import BotmanagerServer


class Botmanager(Command):
    """Run Botmanager server"""

    name = 'botmanager'
    arguments = [
        dict(name='--host', type=str, default='localhost', help='Serving host'),
        dict(name='--port', type=int, default=5401, help='Serving port'),
    ]

    def main(self, args):
        self.log.info(f'Started with arguments: {args}')
        botmanager = BotmanagerServer(args.host, args.port, self.log)
        botmanager.run()
