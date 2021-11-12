from .service import Service
from ..protocol import ApiObject, Attribute
from .exceptions import ServiceError
from pandas import DataFrame
from time import perf_counter, sleep
from tornado.ioloop import IOLoop
import random
import functools
import time
import queries
from datetime import datetime

def model_query(self, body):
    return self.server.model.query(body.text, body.tenant)


async def db_insert_log(self, answers, body):
    qu = self.server.queries.get('SQL_INSERT', 'sql_insert_log')
    conf = None
    ques = None
    self.log.info(answers)
    if answers and answers[0] and 'confidence' in answers[0]:
        conf = answers[0]["confidence"]
    if answers and answers[0] and 'index_ques' in answers[0]:
        ques = answers[0]["index_ques"]
    sqlanswer = await self.server.querysession.query(qu, [datetime.now(), str(body), conf, ques, answers[0]["text"], body.tenant ])
    sqlanswer.free()
    
    

async def db_query(self, answers, body):
    for res in answers:
        #if (res['text'].startswith("zammad:")):
        #   res['text'] = z.get_article(url_zammad.format(res['text'][len("zammad:"):],res['text'][len("zammad:"):]))
        if (res['text'].startswith("query:")):
            # get table (format: query:[table]:[id_answer])  #table is risposte fixed now for security reason
            self.log.info("query get")
            info = res['text'].split(":")
            #sqlanswer = self._readManyParams('sql_read_answer', [info[2],body.tenant])
            qu = self.server.queries.get('SQL_READ', 'sql_read_answer')
            sqlanswer = await self.server.querysession.query(qu, [info[2],body.tenant])

            if not isinstance(sqlanswer, queries.Results) or sqlanswer.count()<=0:
                self.log.info("not found")
                res['text'] = str(self.server.config.get('COMMON', 'invalidanswer'))
            else:
                valid = sqlanswer[0]['validato']
                if (not valid):
                    res['text'] = str(self.server.config.get('COMMON', 'invalidanswer'))
                else:
                    res['text'] = sqlanswer[0]['risposta']
            sqlanswer.free()
    return answers

class Query(Service):

    name = 'query'

    class Body(ApiObject):
        text = Attribute(typ=str, required=True)
        tenant = Attribute(typ=str, required=False, default="-1")

    class Result(ApiObject):
        answers = Attribute(typ=list, required=True)



    async def serve(self, body):
        idRun = "["+str(random.random())+"]"
        self.log.debug(idRun+" Starting serve ")
        t1 = perf_counter()
        #result = await IOLoop.current().run_in_executor(None, slow_func)
        #answers = self.server.model.query(body.text, body.tenant)
        answers =  await IOLoop.current().run_in_executor(None,model_query ,self, body)
        t2 = perf_counter()
        self.log.debug(idRun+"Model query finished in "+str(t2-t1))
        #answers =  await IOLoop.current().run_in_executor(None,db_query,self, answers, body)
        answers = await db_query(self,answers, body)
        t3 = perf_counter()
        self.log.debug(idRun+"Answer from DB in "+str(t3-t2))
        t4 = perf_counter()
        self.log.debug(idRun+"Insert history finished in "+str(t4-t3))
        await db_insert_log(self, answers, body)
        self.log.debug(idRun+"Total in "+str(t4-t1))

        return dict(
            answers=answers
        )



       
    #    await IOLoop.current().run_in_executor(executor=None,func=functools.partial(Query.serve_blocking ,self, body))
