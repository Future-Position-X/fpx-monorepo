from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from singleton_decorator import singleton
from contextlib import contextmanager

@singleton
class DB:
    _session = {}
    def __init__(self):
        pg = create_engine(os.environ.get('DATABASE_URL'))
        Session = sessionmaker(bind=pg)
        self._session = Session(autocommit=True)

    def session(self):
        self._session

    @contextmanager
    def transaction(self):
        self._session.begin(subtransactions=True)
        try:
            yield self._session
        except:
            self._session.rollback()
            raise
        finally:
            self._session.commit()