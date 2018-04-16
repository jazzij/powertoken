"""
Contains the models to be used with the SQLAlchemy database interface.\n
Meant to be used by the background scripts, not the Flask app.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 4/13/2018.
"""

from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

DB_PATH = "data/pt.db"
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

class User(Base):
	"""
	Represents a PowerToken user who is in recovery.
	"""
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	username = Column(String(32), nullable=False, index=True, unique=True)
	registered_on = Column(DateTime, index=True, default=datetime.now())
	goal_period = Column(String(16), default="daily")
	wc_id = Column(Integer, unique=True)
	wc_token = Column(String(128))
	fb_token = Column(String(256))
	logs = relationship("Log", backref="user", lazy="dynamic")
	activities = relationship("Activity", backref="user", lazy="dynamic")
	errors = relationship("Error", backref="user", lazy="dynamic")
	days = relationship("Day", backref="user", lazy="dynamic")

	def __repr__(self):
		return "<User {}>".format(self.username)

class Log(Base):
	"""
	Represents a WEconnect-Fitbit progress log.
	"""
	__tablename__ = "log"
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, index=True, default=datetime.now())
	daily_progress = Column(Float)
	weekly_progress = Column(Float)
	step_count = Column(Integer)
	user_id = Column(Integer, ForeignKey("user.id"))

	def __repr__(self):
		return "<Log {}>".format(self.id)

class Activity(Base):
	"""
	Represents a WEconnect activity.
	"""
	__tablename__ = "activity"
	id = Column(Integer, primary_key=True)
	activity_id = Column(Integer, index=True, unique=True)
	start_time = Column(DateTime, index=True)
	end_time = Column(DateTime, index=True)
	expiration = Column(DateTime, index=True)
	weight = Column(Integer)
	user_id = Column(Integer, ForeignKey("user.id"))
	days_activities = relationship("DaysActivities", backref="activity", lazy="dynamic")

	def __repr__(self):
		return "<Activity {}>".format(self.activity_id)

class Error(Base):
	"""
	Represents an error that occurred somewhere in the background scripts.
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
		return "<Error '{}' for user {}>".format(self.message, self.user.username)

class Day(Base):
	"""
	Represents a day of progress (which activities are completed, etc).
	"""
	__tablename__ = "day"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime, index=True)
	user_id = Column(Integer, ForeignKey("user.id"))
	days_activities = relationship("DaysActivities", backref="day", lazy="dynamic")

class DaysActivities(Base):
	__tablename__ "daysactivities"
	id = Column(Integer, primary_key=True)
	completed = Column(Boolean)
	day_id = Column(Integer, ForeignKey("day.id"))
	activity_id = Column(Integer, ForeignKey("activity.id"))