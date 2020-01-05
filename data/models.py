"""
Contains the models to be used with the SQLAlchemy database interface.\n
Meant to be used by the background scripts, not the Flask app.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 4/30/2018.

Update March 2019 -  This is a really helpful guide:
https://stackoverflow.com/questions/41004540/using-sqlalchemy-models-in-and-out-of-flask

TODO: 
Create separate ADMIN Model for FLASK with UserMixin, Password hashing
See models_flask.py for details on how
"""

from datetime import datetime
from sqlalchemy import MetaData, Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

metadata = MetaData()
Base = declarative_base(metadata=metadata)

TALLY="tally"
CHARGE="charge"
WEIGHT="weighted progress"
PROGRESS="progress"

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
	id = Column(Integer, primary_key=True)
	username = Column(String(32), nullable=False, index=True, unique=True)
	registered_on = Column(DateTime, index=True, default=datetime.now())
	goal_period = Column(String(16), default=PROGRESS)
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

class Log(Base):
	"""
	Represents a PowerToken progress log, added whenever WEconnect progress is
	detected and Fitbit step count is updated.
	"""
	__tablename__ = "log"
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, index=True, default=datetime.now())
	wc_progress = Column(Float)
	fb_step_count = Column(Integer)
	user_id = Column(Integer, ForeignKey("user.id"))

	def __repr__(self):
		return "<Log {}>".format(self.id)

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
	id = Column(Integer, primary_key=True)
	date = Column(DateTime, index=True)	# Time portion is ignored
	computed_progress = Column(Float, default=0.0) #calculated
	checkin_count = Column(Integer, default = 0) #raw
	user_id = Column(Integer, ForeignKey("user.id"))
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
		
		
if __name__ == "__main__":
	print("Running models.py as main")
	