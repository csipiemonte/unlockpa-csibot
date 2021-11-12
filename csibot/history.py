from .logger import Logger
from datetime import datetime
import logging


class History:

    def __init__(self,
                 name,
                 location='logs',
                 when='midnight',
                 backupCount=0,
                 ext='txt'):
        """
        :param name: name of the logger. It will be used for directory and default file (str)
        :param location: path where save logs
        :param when: when a rollover occurs: S (Seconds), M (Minutes), H (Hours), D (Days), midnight (str)
        :param backupCount: max number of files
        :param ext: extension of files (str)
        """
        self._history = Logger(name,
                               location=location,
                               when=when,
                               backupCount=backupCount,
                               level=logging.INFO,
                               fmt='',
                               ext=ext,
                               stdout=False)

    def insert(self, query, answers):
        """
        Log query, answer into the file
        :param query: Text of given query
        :param answers: List of found answers
        """
        # History txt
        dt = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        row = f'{dt} - {query}\n'
        for i in range(len(answers)):
            text = answers[i].get('text', '')
            for rep in ['\n', '\r']:
                text = text.replace(rep, ' ')
            confidence = answers[i].get('confidence', 0) * 100
            row += f'\t[{confidence:.2f} %] {text}\n'
        row += '\n'
        self._history.info(row)
