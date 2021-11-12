from csibot.cli import classes
from csibot import Logger
import logging
import argparse


if __name__ == "__main__":

    log = Logger('chatbot', level=logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('gensim').setLevel(logging.ERROR)
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    commands = dict(map(lambda cls: (cls.name, cls(subparsers, log)), classes))

    args = parser.parse_args()
    cmd = commands[args.command]

    cmd.main(args)
