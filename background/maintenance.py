"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in CronTab.\n
Created by Abigail Franz on 2/28/2018.\n
Last modified by Jasmine Jones on 6/19/2019.

	Accomplishes 5 maintenance tasks:
	* Deletes all incomplete profiles from the `user` table.
	* If any users have been removed from the database, deletes their 
	  `activity` and `day` (and corresponding `event`) records.
	* If users have added or updated activities, updates the database.
	* Populates each user's `day` and corresponding `event` records for today.
	* Makes sure all users have Fitbit step goals of 1,000,00

"""

from database import get_session, User, clear_db, close_connection

def remove_incomplete_users( session):
	users = session.query(User).all()
	for user in users:
		if (user.wc_id is None) or (user.fb_token is None) or (user.wc_token is None):
			clear_db(user.username)
					
			

def maintain():

	users = session.query(User).all()
	for user in users:
		update_activities(user)
		populate_today(user)
		fitbit.change_step_goal(user, 1000000)

if __name__ == "__main__":
	session = get_session()
	
	remove_incomplete_users(session)
	
	close_connection(session)
