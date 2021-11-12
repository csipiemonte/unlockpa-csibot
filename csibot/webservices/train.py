from ..models import Casew2v, Caseclus, Caseensemble
from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import PathNotFoundError, BotNotFoundError
from os import path
import dill
from tornado.ioloop import IOLoop




class Train(Service):

    name = 'train'

    class Body(ApiObject):
        idbot = Attribute(typ=int, required=True)

    class Result(ApiObject):
        success = Attribute(typ=bool, required=True)

    async def serve(self, body):
         res = await IOLoop.current().run_in_executor(None,train,self,body)
   
    def fit(self, idbot):
        # Get dataframes
        self.log.info('start training')
        bot = self._read('sql_read_bot', idbot)
        if bot.empty:
                raise BotNotFoundError(idbot)
        synonyms = self._read('sql_read_syn', idbot)
        knowledge_base = self._read('sql_read_kb', idbot)
        stopwords = self._read('sql_read_stopwords', idbot)
        compounds = self._read('sql_read_compound', idbot)
        self._commit()
        self._close()
        # Select class of model
        classes = {
                1: Caseclus,
                2: Casew2v,
                3: Caseensemble
        }
        cls = classes.get(bot['num_algo'].get(0), Caseclus)
        self.log.debug(f'Train: Selected class {cls.__name__}')

        # Create model
        model = cls(bot, synonyms, knowledge_base, stopwords, compounds)
        model.fitModel()

        # Save file
        if not path.isdir(self.server.dillpath):
                raise PathNotFoundError(self.server.dillpath)
        dillfile = self._dillfile(self.server.dillpath, idbot)
        with open(dillfile, mode='wb') as fp:
                dill.dump(model, fp)

        return dict(
                success=True
        )
 
