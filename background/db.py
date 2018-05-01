"""
Database module common to the background scripts and their various helpers.\n
Created by Abigail Franz on 4/30/2018.\n
"""

from models import Base, DB_PATH
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up the SQLAlchemy engine and connect it to the Sqlite database.
engine = create_engine("sqlite:///" + DB_PATH)
Base.metadata.bind = engine
DbSession = sessionmaker(bind=engine)
session = DbSession()