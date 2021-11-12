"""
LOG LEVELS
--------------------
CRITICAL     	50
ERROR 	        40
WARNING     	30
INFO         	20
DEBUG 	        10
NOTSET 	         0
"""


from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import logging
import os


class MyTimedRotatingFileHandler(TimedRotatingFileHandler):

    def __init__(self, filename, **kwargs):
        dirName, baseName = os.path.split(filename)
        if dirName:
            os.makedirs(dirName, exist_ok=True)
        super().__init__(filename, **kwargs)
        self.namer = self._namer

    def _namer(self, default):
        dirName, baseName = os.path.split(self.baseFilename)
        ext = os.path.splitext(baseName)[1]
        dtstr = default[len(self.baseFilename + '.'):]
        dt = datetime.strptime(dtstr, self.suffix)
        dtformat = self.suffix + ext
        return os.path.join(dirName, dt.strftime(dtformat))

    def getFilesToDelete(self):
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        for fileName in fileNames:
            if self.extMatch.match(fileName):
                result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


class Logger(logging.getLoggerClass()):

    def __init__(self,
                 name,
                 location='logs',
                 when='midnight',
                 backupCount=365,
                 level=logging.INFO,
                 fmt='%(asctime)s - %(levelname)-8s - "%(message)s"',
                 ext='log',
                 stdout=True):
        """
        :param name: name of the logger. It will be used for directory and default file (str)
        :param location: path where save logs
        :param when: when a rollover occurs: S (Seconds), M (Minutes), H (Hours), D (Days), midnight (str)
        :param backupCount: max number of files
        :param level: CRITICAL, ERROR, WARNING, INFO, DEBUG (int)
        :param fmt: formatter of row (str)
        :param ext: extension of files (str)
        :param stdout: if True, log to the console too (boolean)
        """
        super().__init__(name)
        self.setLevel(level)

        #  File handler
        filename = os.path.join(location, name, f'{name}.{ext}')
        fh = MyTimedRotatingFileHandler(filename, when=when, backupCount=backupCount)
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter(fmt))
        self.addHandler(fh)

        # Standard output
        if stdout:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(logging.Formatter(fmt))
            self.addHandler(ch)

    def httpLogger(self, handler):
        """
        Method called from Application when status_code < 400
        and passed to it by arg 'log_function' in settings parameter
        :param handler: Handler object
        """
        self.debug(f'{handler.get_status()} - {handler._request_summary()}')
