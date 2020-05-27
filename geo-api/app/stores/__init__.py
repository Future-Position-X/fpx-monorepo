from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

pg = create_engine(os.environ.get('DATABASE_URL'))
Session = sessionmaker(bind=pg)
session = Session()
