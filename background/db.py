"""
Database module common to the background scripts and their various helpers.\n
Created by Abigail Franz on 4/30/2018.\n
Last Modified by Abigail Franz on 5/9/2018.
"""

from models import Base
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("DATABASE_URL") or \
	"sqlite:///" + os.path.join(basedir, "data/pt-fade.db")

# Set up the SQLAlchemy engine and connect it to the Sqlite database.
engine = create_engine(DB_PATH)
Base.metadata.bind = engine
DbSession = sessionmaker(bind=engine)
session = DbSession()