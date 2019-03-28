"""
Database.py
Initialization and such, as described by 
http://flask.pocoo.org/docs/1.0/patterns/sqlalchemy/

This script is designed to access a database on the server side (outside of the FLASK application context)
The database schema and models are in data.models.

To create the database, use init_db()
To edit the database, add this statement to your script
	>>from powertoken.database import db_session
	Then user db_session.add(), db_session.delete(), db_session.commit() as needed
	
To close the connection to the database, run closeConnection
	>>from powertoken.database import closeConnection

For more information: https://docs.sqlalchemy.org/en/latest/orm/session_basics.html#basics-of-using-a-session
Last Update March 2019 by Jasmine Jones
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
from data.models import metadata

#basedir = os.path.abspath(os.path.curdir)
#DB_PATH = "sqlite:///" + os.path.join(basedir, "data/pt_data.db")
DB_PATH = "sqlite:///" + os.environ.get("DB_PATH")

# Set up the SQLAlchemy engine and connect it to the Sqlite database
#using poolclass=NullPool makes it so that the entire connection to the database is cut when the session is closed
engine = create_engine(DB_PATH, poolclass=NullPool)
DBSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

db_session = DBSession()


def init_db(engine):
	'''import all application models here so registered with metadata
	'''
	from data.models import User, Activity, Event, Log, Day, Admin, Error
	metadata.create_all(engine)
	
def printTables():
	''' So you can see the database tables in pt_data.db
	 See models.py for tables written out in class format
	 '''
	tables = metadata.tables
	print(tables['activity'])
	print(tables['user'])
	print(tables['event'])
		
def closeConnection():
	'''Use this function to kill all threads and make sure the sessions are closed
	'''
	db_session.close()




if __name__ == "__main__":
	print("Running background/database.py as main")	
	init_db(engine)
	printTables()
	closeConnection()