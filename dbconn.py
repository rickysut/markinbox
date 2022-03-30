import sys
import pymysql as db
import gevent
from pymysql import cursors
from gevent.queue import Queue


import logging

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("dbconn")

class mysql_db:

    def __init__(self, db_config, time_to_sleep=30, test_run=False):
        self.username = db_config.get('user')
        self.password = db_config.get('password')
        self.host = db_config.get('host')
        self.database = db_config.get('database')
        self.max_pool_size = 20
        self.test_run = test_run
        self.pool = None
        self.time_to_sleep = time_to_sleep
        self._initialize_pool()
        
    def _initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)
        current_pool_size = self.pool.qsize()
        if current_pool_size < self.max_pool_size:  # this is a redundant check, can be removed
            for _ in range(0, self.max_pool_size - current_pool_size):
                try:
                    self.conn = db.connect(host=self.host,
                                           user=self.username,
                                           password=self.password,
                                           database=self.database,
                                           cursorclass=cursors.DictCursor)
                    self.pool.put_nowait(self.conn)

                except db.OperationalError as e:
                    LOGGER.error(
                        "Cannot initialize connection pool - retrying in {} seconds".format(self.time_to_sleep))
                    LOGGER.exception(e)
                    break
        self._check_for_connection_loss()

    def get_initialized_connection_pool(self):
        return self.pool

    def get_connection(self):
        self._check_for_connection_loss()
        return self.conn

    def _re_initialize_pool(self):
        gevent.sleep(self.time_to_sleep)
        self._initialize_pool()

    def _check_for_connection_loss(self):
        self.conn.ping(True)
        #while True:
        #    self.conn = None
        #    if self.pool.qsize() > 0:
        #        self.conn = self.pool.get()

        #    if not self._ping(self.conn):
        #        if self.test_run:
        #            self.port = 3306

        #        self._re_initialize_pool()

        #    else:
        #        self.pool.put_nowait(self.conn)

        #    if self.test_run:
        #        break
        #    gevent.sleep(self.time_to_sleep)

    def _ping(self, conn):
        try:
            if conn is None:

                conn = db.connect(host=self.host,
                                  user=self.username,
                                  password=self.password,
                                  database=self.database,
                                  cursorclass=cursors.DictCursor)
            cursor = conn.cursor()
            cursor.execute('select 1;')
            LOGGER.debug(cursor.fetchall())
            return True

        except db.OperationalError as e:
            LOGGER.warn(
                'Cannot connect to mysql - retrying in {} seconds'.format(self.time_to_sleep))
            LOGGER.exception(e)
            return False

    def _commit(self):
        self.conn.commit()
