"""
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in Crontab, probably every 15 minutes.
Created by Abigail Franz on 2/28/2018
Last modified by Abigail Franz on 3/16/2018
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from background.models import Base, User, Activity, Log, DB_PATH
from background.weconnect import WeConnect
from background.fitbit import Fitbit
from background.helpers import get_users_with_current_activities

# Configures logging for the module
logger = logging.getLogger("background.polling")
logger.setLevel(logging.INFO)
logpath = "/export/scratch/powertoken/data/background.polling.log"
handler = logging.FileHandler(logpath)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)-4s - %(message)s")
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
	"""
	users = get_users_with_current_activities(session)
	if users is None:
		logger.info("No current activities. Returning.")
		return
	for user in users:
		wc = WeConnect(user.wc_id, user.wc_token, user.goal_period)
		fb = Fitbit(user.fb_token, user.goal_period)
		
		# Gets progress (as a decimal percentage) from WEconnect.
		progress = 0.0
		daily_progress, weekly_progress = wc.poll()
		if user.goal_period == "daily":
			progress = daily_progress
		else:
			progress = weekly_progress

		# If the poll request succeeded, updates Fitbit and adds a new entry to
		# the logs.
		if progress == -1:
			logger.error("\tCouldn't get progress for user %s.", user.username)
		elif progress == 0:
			logger.info("\tUser %s has no progress yet today.", user.username)
		else:
			step_count = fb.reset_and_update(progress)
			if step_count == -1:
				logger.error("\tCouldn't update Fitbit for user %s.", user.username)
			else:
				log = Log(daily_progress = daily_progress, 
						weekly_progress = weekly_progress,
						step_count = step_count, user = user)
				session.add(log)
				session.commit()

if __name__ == "__main__":
	logger.info("Running the poll-and-update loop...")
	poll_and_update()
	logger.info("...Done.")