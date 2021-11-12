from .service import Service
from .train import Train
from ..protocol import ApiObject, Attribute
from datetime import datetime
from tornado.ioloop import IOLoop

def train_in_insert(log,server,idbot):
    log.info("start train method")
    train = Train(server)
    train.fit(idbot)
    log.info("end train")
    return
            
class Insert(Service):

    name = 'insert'

    class Body(ApiObject):

        class RowBot(ApiObject):
            description = Attribute(typ=str, required=True)
            bot_version = Attribute(typ=int, required=True)
            num_algo = Attribute(typ=int, required=True)
            confidence_tfidf = Attribute(typ=float, required=False, default=0.3)
            confidence_lsa = Attribute(typ=float, required=False, default=0.4)
            is_lsa_sim = Attribute(typ=bool, required=False, default=False)
            n_topics = Attribute(typ=int, required=False, default=0)
            is_cluster = Attribute(typ=bool, required=False, default=False)
            n_cluster = Attribute(typ=int, required=False, default=0)
            confidence_wv = Attribute(typ=float, required=False, default=0.691)
            wordvec_path = Attribute(typ=str, required=False, default='')

        class RowKnowledgeBase(ApiObject):
            question_type = Attribute(typ=str, required=True)
            question_number = Attribute(typ=str, required=True)
            question = Attribute(typ=str, required=True)
            answer = Attribute(typ=str, required=True)
            note = Attribute(typ=str, required=False)

        class RowStopword(ApiObject):
            stopword = Attribute(typ=str, required=True)
            to_keep = Attribute(typ=bool, required=True)

        class RowCompoundWord(ApiObject):
            compound_word = Attribute(typ=str, required=True)
            base_token = Attribute(typ=str, required=True)

        class RowSynonymWord(ApiObject):
            synonym_word = Attribute(typ=str, required=True)
            base_token = Attribute(typ=str, required=True)

        bot = Attribute(typ=RowBot, required=True)
        knowledge_base = Attribute(typ=[RowKnowledgeBase], required=True)
        stopwords = Attribute(typ=[RowStopword], required=True)
        compound_words = Attribute(typ=[RowCompoundWord], required=True)
        synonym_words = Attribute(typ=[RowSynonymWord], required=True)

    class Result(ApiObject):
        idbot = Attribute(typ=int, required=True)

    async def serve(self, body):
        self.log.info('start insert')
        ts = datetime.now()
        id_bot = self._insert('sql_insert_bot', [body.bot], return_id=True, ts_creation=ts)
        self._insert('sql_insert_kb', body.knowledge_base, ts_creation=ts, id_bot=id_bot)
        self._insert('sql_insert_stopwords', body.stopwords, ts_creation=ts, id_bot=id_bot)
        self._insert('sql_insert_compound', body.compound_words, ts_creation=ts, id_bot=id_bot)
        self._insert('sql_insert_syn', body.synonym_words, ts_creation=ts, id_bot=id_bot)
        self._commit()
        self._close()
        self.log.info('iin insert')
        await IOLoop.current().run_in_executor(None,train_in_insert,self.log,self.server,id_bot)
        self.log.info('fine train')
        return dict(
            idbot=id_bot,
        )

