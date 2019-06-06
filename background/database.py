#imports for database engine
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session, sessionmaker

#imports for models
from datetime import datetime
from sqlalchemy import MetaData, Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#CONSTANTS
DB_REL_PATH = "sqlite:///" + "data/pt_data.db"
DB_PATH = "sqlite:///" + os.environ.get("DB_PATH")

TALLY="tally"
CHARGE="charge"
WEIGHT="weight"
PLAN="plan"

Base = declarative_base()
	
class Admin(Base):
	"""
	Represents a PowerToken administrator, capable of viewing the admin
	dashboard and supervising user progress.
	"""
	__tablename__ = "admin"
	id = Column(Integer, primary_key=True)
	username = Column(String(32), nullable=False, index=True, unique=True)
	email = Column(String(64), nullable=False, index=True, unique=True)
	password_hash = Column(String(128))

	def __repr__(self):
		return "<Admin {}>".format(self.username)
		
	def __init__(self, username):
		self.username = username

class User(Base):
	"""
	Represents a PowerToken user who is in recovery.
	"""
	__tablename__ = "user"
	__table_args__ = {'extend_existing':True} 
	id = Column(Integer, primary_key=True)
	username = Column(String(32), nullable=False, index=True, unique=True)
	registered_on = Column(DateTime, index=True, default=datetime.now())
	metaphor = Column(String(16), default=PLAN)
	wc_id = Column(Integer, unique=True)
	wc_token = Column(String(128))
	fb_token = Column(String(256))
	logs = relationship("Log", backref="user", lazy="dynamic")
	activities = relationship("Activity", backref="user", lazy="dynamic")
	errors = relationship("Error", backref="user", lazy="dynamic")
	days = relationship("Day", backref="user", lazy="dynamic")

	def thisday(self):
		d = datetime.now()
		today = datetime(d.year, d.month, d.day)
		return self.days.filter(Day.date == today).first()

	def __repr__(self):
		return "<User {}>".format(self.username)
	
	def __init__(self, username):
		self.username = username

class Activity(Base):
	"""
	Represents a WEconnect activity.
	"""
	__tablename__ = "activity"
	id = Column(Integer, primary_key=True)
	wc_act_id = Column(Integer, index=True, unique=True)
	name = Column(String(256))
	expiration = Column(DateTime, index=True)
	weight = Column(Integer, default=3)
	user_id = Column(Integer, ForeignKey("user.wc_id"))
	events = relationship("Event", backref="activity", lazy="dynamic")

	def __repr__(self):
		return "<Activity '{}'>".format(self.name)
	

class Error(Base):
	"""
	Represents an error that occurred somewhere in the application(s).
	"""
	__tablename__ = "error"
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, default=datetime.now())
	summary = Column(String(64))
	origin = Column(String(256))
	message = Column(String(256))
	traceback = Column(String(1048))
	user_id = Column(Integer, ForeignKey("user.id"))

	def __repr__(self):
		return "<Error '{}', '{}'>".format(self.summary, self.message)

class Day(Base):
	"""
	Represents a day of progress (which activities are completed, etc).
	"""
	__tablename__ = "day"
	__table_args__ = {'extend_existing':True} 
	id = Column(Integer, primary_key=True)
	date = Column(DateTime, index=True)	# Time portion is ignored
	computed_progress = Column(Float, default=0.0) #calculated
	user_id = Column(Integer, ForeignKey("user.id"))
	complete_count = Column(Integer, default = 0) #raw
	events = relationship("Event", backref="day", lazy="dynamic")

	def __repr__(self):
		return "<Day {}>".format(self.date.strftime("%Y-%m-%d"))

class Event(Base):
	"""
	Represents a WEconnect event (an activity on a particular date).
	"""
	__tablename__ = "event"
	id = Column(Integer, primary_key=True)
	eid = Column(String, index=True)
	start_time = Column(DateTime) # Date portion is ignored
	end_time = Column(DateTime)	# Date portion is ignored
	completed = Column(Boolean)
	day_id = Column(Integer, ForeignKey("day.id"))
	activity_id = Column(Integer, ForeignKey("activity.wc_act_id"))

	def __repr__(self):
		output = "<Event '{}'>".format(self.eid)
		return output


''' --------- ####

'''
# Set up the SQLAlchemy engine and connect it to the Sqlite database
#using poolclass=NullPool makes it so that the entire connection to the database is cut when the session is closed
#engine = create_engine(DB_REL_PATH, poolclass=NullPool)
def get_engine():
	engine = create_engine(DB_PATH, poolclass=NullPool)
	return engine

def get_metadata():
	engine = get_engine()
	Base.metadata.reflect(engine)
	return Base.metadata

def get_session():
	engine = get_engine()
	DBSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
	db_session = DBSession()
	return db_session


#SETUP - RUN ONCE
def setup_db():
	'''
	For some reason this doesn't work, so use 
	/createDB route via flask instead
	'''
	mt = MetaData()
	Base = declarative_base(metadata=mt)
	engine = get_engine()
	Base.metadata.create_all(engine)	

#TEST 
def printTables():
	''' So you can see the database tables in pt_data.db
	 See models.py for tables written out in class format
	 '''
	metadata = get_metadata()
	User = metadata.tables['user']
	Day = metadata.tables['day']
	Activity = metadata.tables['activity']
	Event = metadata.tables['event']
	[print(c.name) for c in Day.columns]
	[print(d.name) for d in User.columns]
	[print(e.name) for e in Event.columns]
	[print(f.name) for f in Activity.columns]


if __name__ == "__main__":
	print("Running new database as main")
	printTables()