"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in CronTab.\n
Created by Abigail Franz on 2/28/2018.\n
Last modified by Abigail Franz on 5/5/2018.
"""

from db import session
import fitbit
from helpers import (populate_today, remove_expired_activities, 
		remove_incomplete_users, update_activities)
from models import User

def maintain():
	"""
	Accomplishes 5 maintenance tasks:
	* Deletes all incomplete profiles from the `user` table.
	* If any users have been removed from the database, deletes their 
	  `activity` and `day` (and corresponding `event`) records.
	* If users have added or updated activities, updates the database.
	* Populates each user's `day` and corresponding `event` records for today.
	* Makes sure all users have Fitbit step goal of 1,000,00

	"""
	remove_incomplete_users()
	remove_expired_activities()
	users = session.query(User).all()
	for user in users:
		update_activities(user)
		populate_today(user)
		fitbit.change_step_goal(user, 1000000)

if __name__ == "__main__":
	maintain()