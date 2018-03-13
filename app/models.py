"""
Contains the models to be used with the SQLAlchemy database interface.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 3/13/2018.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

#GoalPeriod = Enum("daily", "weekly")

@login.user_loader
def load_admin(id):
	return Admin.query.get(int(id))

class Admin(UserMixin, db.Model):
	"""
	Represents a PowerToken administrator, capable of viewing the admin
	dashboard and supervising user progress.
	"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)		

	def __repr__(self):
		return "<Admin {}>".format(self.username)

class User(db.Model):
	"""
	Represents a PowerToken user who is in recovery.
	"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	registered_on = db.Column(db.DateTime, index=True, default=datetime.now())
	goal_period = db.Column(db.String(16), default="daily")
	wc_id = db.Column(db.Integer, unique=True)
	wc_token = db.Column(db.String(128))
	fb_token = db.Column(db.String(256))
	logs = db.relationship("Log", backref="user", lazy="dynamic")
	activities = db.relationship("Activity", backref="user", lazy="dynamic")

	def __repr__(self):
		return "<User {}>".format(self.username)

class Log(db.Model):
	"""
	Represents a WEconnect-Fitbit progress log.
	"""
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	daily_progress = db.Column(db.Float)
	weekly_progress = db.Column(db.Float)
	step_count = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

	def __repr__(self):
		return "<Log {}>".format(self.id)

class Activity(db.Model):
	"""
	Represents a WEconnect activity.
	"""
	id = db.Column(db.Integer, primary_key=True)
	activity_id = db.Column(db.Integer, index=True, unique=True)
	start_time = db.Column(db.DateTime, index=True)
	end_time = db.Column(db.DateTime, index=True)
	expiration = db.Column(db.DateTime, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

	def __repr__(self):
		return "<Activity {}>".format(self.activity_id)