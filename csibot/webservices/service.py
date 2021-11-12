import traceback
from .exceptions import DBConnectionError, DBOperationError, ServiceDictError
from os import path
from pandas import DataFrame
import re
from tornado import gen

class Service:

    name = 'default'  # Replace it
    Body = None
    Result = None

    def __init__(self, server):
        self.server = server
        self.log = self.server.log
        self.request = None
#async
    async def __call__(self, dict_body, request):
        self.request = request
        try:
            body = self.Body(dict_body)
            res = await self.serve(body) #await
            return  self.Result(res)
        except (TypeError, KeyError) as e:
            self.log.error(e)
            track = traceback.format_exc()
            print("#### ORIGINAL EXCEPTION:"+ str(track))
            raise ServiceDictError(self.name, str(e))

    def _readManyParams(self, queryname, params):
        """
        Internal function for call read of dbconnection
        :param queryname: name of query in ini configuration (str)
        :param id_table: the id to filter rows in the select table
        :return: dataframe
        """
        sql = self.server.queries.get('SQL_READ', queryname)
        try:
            return self.server.dbconnection.readManyParams(sql, params)
        except Exception as e:
            self._rollback(e)

    def _read(self, queryname, id_table):
        """
        Internal function for call read of dbconnection
        :param queryname: name of query in ini configuration (str)
        :param id_table: the id to filter rows in the select table
        :return: dataframe
        """
        sql = self.server.queries.get('SQL_READ', queryname)
        try:
            return self.server.dbconnection.read(sql, id_table)
        except Exception as e:
            self._rollback(e)

    def _insert(self, queryname, data, return_id=False, **extras):
        """
        Internal function for call insert of dbconnection
        :param queryname: name of query in ini configuration (str)
        :param dframe: pandas dataframe
        :param return_id: if you want the inserted ID back (bool)
        :param extras: set value of fields that aren't in data but in query
        :return: success
        """
        sql = self.server.queries.get('SQL_INSERT', queryname)
        m = re.match("insert into (?P<table>\w+) ?\((?P<columns>[\S ]+)\)", sql, flags=re.IGNORECASE)
        columns = re.sub(' ', '', m.group('columns')).split(',')
        dframe = DataFrame(data, columns=columns)
        for key, value in extras.items():
            dframe[key] = value
        try:
            return self.server.dbconnection.insert(sql, dframe, return_id=return_id)
        except Exception as e:
            self._rollback(e)

    def _update(self, queryname, id_table):
        """
        Internal function for call read of dbconnection
        :param queryname: name of query in ini configuration (str)
        :param id_table: the id to select records to update
        :return: success
        """
        sql = self.server.queries.get('SQL_UPDATE', queryname)
        try:
            return self.server.dbconnection.update(sql, id_table)
        except Exception as e:
            self._rollback(e)

    def _delete(self, queryname, id_table):
        """
        Internal function for call read of dbconnection
        :param queryname: name of query in ini configuration (str)
        :param id_table: the id to filter rows in the select table
        :return: success
        """
        sql = self.server.queries.get('SQL_DELETE', queryname)
        try:
            return self.server.dbconnection.remove(sql, id_table)
        except Exception as e:
            self._rollback(e)

    def _commit(self):
        """
        Internal function for commit updates on dbconnection
        """
        try:
            self.server.dbconnection.commit()
        except Exception as e:
            self._rollback(e)

    def _rollback(self, error):
        """
        Internal function for rollback updates on dbconnection
        """
        self.log.error(error)
        try:
            self.server.dbconnection.rollback()
        finally:
            raise DBOperationError(error)

    def _close(self):
        """
        Internal function for close connection
        """
        try:
            self.server.dbconnection.close()
        except Exception as e:
            raise DBConnectionError()

    @staticmethod
    def _dillfile(dillpath, idbot):
        """
        Format file path as dillpath/idbot.sav
        :param dillpath: directory of all files serialized (str)
        :param idbot: id bot (int)
        :return: path of file
        """
        return path.join(dillpath, f'{idbot:0>4d}.sav')

    def serve(self, body):
        """
        Replace this method in every class
        :param body: input body
        :return: result
        """
        raise NotImplemented(f'Method "serve" is not implemented in service {self.name}')

    def close(self):
        """
        Replace this method for do something after responce
        """
        pass
