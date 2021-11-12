from configparser import ConfigParser, RawConfigParser
import nltk
from os import environ 
import warnings

config = ConfigParser()
config.read('config.ini')

# Import edited settings from ENV
config.set('DB', 'DBHOST', environ['POSTGRES_URL'])
config.set('DB', 'DBPORT', environ['POSTGRES_PORT'])
config.set('DB', 'PASSWORD', environ['POSTGRES_PASSWORD'])
config.set('DB', 'USER', environ['POSTGRES_USER'])
config.set('DB', 'DATABASE', environ['POSTGRES_DB'])
config.set('DB', 'SCHEMA', environ['POSTGRES_SCHEMA'])


configSql = RawConfigParser()
configSql.read('configSql.ini')
nltk.data.path.append(config.get('NLTK', 'path', fallback=None))

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
