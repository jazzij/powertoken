"""
Database module common to the background scripts and their various helpers.\n
Created by Abigail Franz on 4/30/2018.\n
"""

from models import Base
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = os.environ.get("SQLALCHEMY_DATABASE_URL")

# Set up the SQLAlchemy engine and connect it to the Sqlite database.
engine = create_engine(DB_PATH)
Base.metadata.bind = engine
DbSession = sessionmaker(bind=engine)
session = DbSession()