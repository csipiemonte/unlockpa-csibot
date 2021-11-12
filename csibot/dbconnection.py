import psycopg2
from psycopg2.extras import execute_values
import pandas.io.sql as psql
import logging

class Dbconnection:

    def __init__(self, schema, database, user, password, dbhost, dbport, log=None):
        self._properties = dict(
            database=database,
            user=user,
            password=password,
            host=dbhost,
            port=dbport,
            options=f'-c search_path={schema}'
        )
        self._conn = psycopg2.connect(**self._properties)
        self.log = log

    @property
    def conn(self):
        if self._conn and not self._conn.closed:
            return self._conn
        else:
            self._conn = psycopg2.connect(**self._properties)
            return self._conn

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()

    def commit(self):
        # Commit della connection a DB (altrimenti le modifiche effettuate non vengono applicate sul database)
        self.conn.commit()

    def rollback(self):
        # Rollback to clean wrong DB modifications
        self.conn.rollback()

    def read(self, sql, idTable):
        """
        :param sql: read sql to execute
        :param idTable: the id to filter rows in the select table
        :return: a dataframe of the selected rows, -1 otherwise
        """
        try:
            return(psql.read_sql(sql, self.conn,params={idTable}))
        except Exception as e:
            self.log.error(e)
            return(-1)

    def readManyParams(self, sql, params):
        """
        :param sql: read sql to execute
        :param idTable: the id to filter rows in the select table
        :return: a dataframe of the selected rows, -1 otherwise
        """
        try:
            self.log.info("readManyParams:"+sql+"["+str(params)+"]")
            return(psql.read_sql(sql, self.conn,params=params))
        except Exception as e:
            self.log.error(e)
            return(-1)

    def insert(self, sql, dframe,return_id = False):
        """
        :param sql: insert query to execute
        :param dframe: data_frame to insert in the database
                       Columns order and types must be coherent with the input SQL
        :param return_id: Bool if you want the inserted ID back
        :return: the inserted ID
        """
        with self.conn.cursor() as c:
            values_list = [tuple(x) for x in dframe.values]
            # Execute multiple insert
            execute_values(c, sql, values_list)
            # If main table retrieve autoincrement ID
            if return_id:
                id_out = c.fetchone()[0]
                return(id_out)

    def update(self, sql, idTable):
      """
      :param sql: update_sql query
      :param idTable: id to select records to update
      :return:  None
      """
      with self.conn.cursor() as c:
          c.execute(sql, (idTable,))


    def remove(self, delete_sql, idTable):
        """
        :param delete_sql: delete sql to execute
        :param idTable: the id of the rows to delete
        """
        with self.conn.cursor() as c:
            c.execute(delete_sql, (idTable,))

