"""
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in Crontab, probably every 5-15 minutes.\n
Created by Abigail Franz on 2/28/2018.\n
Last modified by Abigail Franz on 5/2/2018.
"""

from db import session
import fitbit
from helpers import compute_days_progress
from models import Activity, Event, User
import weconnect

def poll_and_update():
	"""
	For each user in the database:
	1. Poll WEconnect to find out how many of the user''s events for today
	   have been completed.
	2. Compute the user's progress for today.
	2. If the user has made progress since the last time this script was run,
	   send the new progress to Fitbit as a walking activity with the following
	   number of steps: progress * 1,000,000.
	"""
	users = session.query(User).all()
	for user in users:
		# API call to WEconnect activities-with-events
		activity_events = weconnect.get_todays_events(user)

		# Keep track of which events have didCheckin set to True
		for activity in activity_events:
			for ev in activity["events"]:
				if ev["didCheckin"]:
					event = session.query(Event).filter(Event.eid == ev["eid"])
					event.completed = True
		session.commit()

		# Compute progress with fade function
		thisday = user.thisday()
		progress = compute_days_progress(thisday)
		if not thisday.computed_progress == progress:
			thisday.computed_progress = progress
			session.commit()
			# Send progress to Fitbit
			step_count = fitbit.update_progress(user, progress)

if __name__ == "__main__":
	poll_and_update()