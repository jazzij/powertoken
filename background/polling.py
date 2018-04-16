"""
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in Crontab, probably every 5-15 minutes.\n
Created by Abigail Franz on 2/28/2018.\n
Last modified by Abigail Franz on 4/6/2018.
"""

from datetime import datetime, timedelta
from logging import getLogger, FileHandler, Formatter, INFO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fitbit import Fitbit
from helpers import get_users_with_current_activities
from models import Base, User, Activity, Log, DB_PATH
from weconnect import WeConnect

# Configures logging for the module
logger = getLogger("background.polling")
logger.setLevel(INFO)
logpath = "/export/scratch/powertoken/data/background.polling.log"
handler = FileHandler(logpath)
handler.setLevel(INFO)
formatter = Formatter("%(asctime)s: %(levelname)-4s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Sets up the SQLAlchemy engine and connects it to the Sqlite database. 
engine = create_engine("sqlite:///" + DB_PATH)
Base.metadata.bind = engine
DbSession = sessionmaker(bind=engine)
session = DbSession()

def poll_and_update():
	"""
	If any activities start or end within the next 15 minutes, add the user who 
	owns them to a list. Then poll all the users in the list for progress.

	As of 4/6/2018, I'm changing it to poll all the users. I was having trouble
	with only polling when I have upcoming or in-progress activities, as I don't
	always "check in" when I'm supposed to. We can always change it back if we
	need to by uncommenting the first line (below this) and commenting out the
	second.
	"""
	#users = get_users_with_current_activities(session)
	users = session.query(User).all()
	if users is None or len(users) == 0:
		logger.info("No current activities. Returning.")
		return
	for user in users:
		wc = WeConnect(user, session)
		fb = Fitbit(user, session)
		
		# Gets progress (as a decimal percentage) from WEconnect.
		progress = 0.0
		daily_progress, weekly_progress = wc.poll()
		if user.goal_period == "daily":
			progress = daily_progress
		else:
			progress = weekly_progress

		# If the poll request succeeded, updates Fitbit and adds a new entry to
		# the logs.
		if progress is None:
			logger.error("\tCouldn't get progress for %s.", user)
		elif progress == 0:
			logger.info("\t%s has no progress yet today.", user)
		else:
			step_count = fb.reset_and_update(progress)
			if step_count is None:
				logger.error("\tCouldn't update Fitbit for %s.", user)
			else:
				log = Log(daily_progress = daily_progress, 
						weekly_progress = weekly_progress,
						step_count = step_count, user = user)
				session.add(log)
				session.commit()
				logger.info("\tUpdated progress for %s.", user)

if __name__ == "__main__":
	logger.info("Running the poll-and-update loop...")
	poll_and_update()
	logger.info("...Done.")
