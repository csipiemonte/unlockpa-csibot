from .command import Command
from ..client import Client


class Monitor(Command):
    """List of all active instances of chatbot"""

    name = 'monitor'
    arguments = [
        dict(name='--endpoint', type=str, default='http://localhost:5401', help='Botmanager endpoint'),
    ]

    def main(self, args):
        self.log.info(f'Started with arguments: {args}')

        botmanager_client = Client(args.endpoint)
        result = botmanager_client.post('monitor')
        self.log.info(result)
