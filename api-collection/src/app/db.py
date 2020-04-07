import psycopg2
from psycopg2.extras import RealDictCursor
import os


def get_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URI'))


class StoreException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors


# domains

class Collection():
    def __init__(self, name):
        self.name = name


# base store class
class Store():
    def __init__(self):
        try:
            self.conn = get_connection()
        except Exception as e:
            raise StoreException(*e.args, **e.kwargs)
        self._complete = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        # can test for type and handle different situations
        self.close()

    def complete(self):
        self._complete = True

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise StoreException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise StoreException(*e.args)


class CollectionStore(Store):

    def find_all(self):
        try:
            c = self.conn.cursor(cursor_factory=RealDictCursor)
            # this needs an appropriate table
            c.execute('SELECT * FROM collections')
            return c.fetchall()

        except Exception as e:
            raise StoreException('error finding all collections', e)
