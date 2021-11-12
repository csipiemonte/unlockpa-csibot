import logging


class Command:
    """Abstract class command"""

    name = None
    arguments = []

    def __init__(self, subparsers, log):
        self.log = log or logging.Logger('default log', level=logging.DEBUG)
        subparser = subparsers.add_parser(self.name, help=self.__doc__)
        for arg in self.arguments:
            name = arg.pop('name')
            subparser.add_argument(name, **arg)
