"""
>> DEPRECATED MARCH 2019. FIND UPDATED file in ~/background/database.py
Database.py
Initialization and such, as described by 
http://flask.pocoo.org/docs/1.0/patterns/sqlalchemy/

This script is designed to power database called outside of the FLASK application context
To create the database, use init_db()
To edit the database, add this statement to your script
	>>from powertoken.database import db_session
	Then user db.session.add(), db.session.commit() as needed

"""
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

basedir = os.path.abspath(os.path.curdir)
DB_PATH = "sqlite:///" + os.path.join(basedir, "data/pt_data.db")

# Set up the SQLAlchemy engine and connect it to the Sqlite database
#using poolclass=NullPool makes it so that the entire connection to the database is cut when the session is closed
engine = create_engine(DB_PATH, poolclass=NullPool)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
Base.metadata.reflect(bind=engine)

metadata = MetaData()
metadata.reflect(bind=engine)

def init_db():
	#import all application models here so registered with metadata
	from powertoken.models import User, Activity, Event, Log, Day, Admin, Error
	Base.metadata.create_all(bind=engine)
	
def printTables():
	''' So you can see the database tables in pt_data.db
	 See models.py for tables written out in class format
	 '''
	for table in Base.metadata.tables():
		print(table)
		
def closeConnection():
	'''Use this function to kill all threads and make sure the sessions are closed
	'''
	db_session.close()
	
	