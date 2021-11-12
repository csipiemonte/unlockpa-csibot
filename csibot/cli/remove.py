from .command import Command
from ..client import Client


class Remove(Command):
    """Delete one bot from database"""

    name = 'remove'
    arguments = [
        dict(name='--endpoint', type=str, default='http://localhost:5401', help='Botmanager endpoint'),
        dict(name='--idbot', type=int, help='Bot id')
    ]

    def main(self, args):
        self.log.info(f'Started with arguments: {args}')

        botmanager_client = Client(args.endpoint)
        result = botmanager_client.post('remove', idbot=args.idbot)

        self.log.info(result)
