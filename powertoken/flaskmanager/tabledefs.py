from datetime import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, DateTime, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///export/scratch/ptdata/pt.db', echo=True)
Base = declarative_base()

class PtUser(Base):
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String)
	registered_on = Column(DateTime)
    goal_period = Column(String)
	wc_id = Column(String)
	wc_token = Column(String)
	fb_token = Column(String)

    def __init__(self, username):
        self.username = username
        self.registered_on = datetime.now()

class PtLog(Base):
	__tablename__ = "logs"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer) # later we'll make this a foreign key
	timestamp = Column(DateTime)
	wc_progress = Column(Float)
	fb_step_count = Column(Integer)

	def __init__(self, user_id, wc_progress, fb_step_count):
		self.user_id = user_id
		self.wc_progress = wc_progress
		self.fb_step_count = fb_step_count
		self.timestamp = datetime.now()
 
# create tables
Base.metadata.create_all(engine)