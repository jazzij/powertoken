"""
Contains some helper functions for the background scripts.
Created by Abigail Franz on 3/16/2018
Last modified by Abigail Franz on 3/26/2018
"""

from datetime import datetime, timedelta, MAXYEAR
from weconnect import WC_FORMAT
from models import User, Activity

def add_or_update_activity(session, activity, user):
	"""
	Insert new activity row into the database if it doesn't already exist and
	is not expired. If it exists but has been updated, update it in the
	database. Return True if activity was inserted or updated and False if it 
	was not.

	:param sqlalchemy.orm.session.Session session: the database session\n
	:param dict activity: an activity from WEconnect in JSON format\n
	:param background.models.User user: the user to which the activity belongs
	"""
	# Determines the start and end times and expiration date (if any)
	st, et, expiration = extract_params(activity)
	act_id = activity["activityId"]

	# Boolean indicating whether or not the activity was inserted/updated
	status = False

	# Ignores the activity if it's already expired
	if expiration <= datetime.now():
		status = False
	else:
		# If the activity already exists in the database, sees if it's been
		# modified recently. If yes, updates it. If not, ignores it.
		existing = session.query(Activity).filter(
			Activity.activity_id == act_id).first()
		if existing:
			modified = datetime.strptime(activity["dateModified"], WC_FORMAT)
			if modified >= datetime.now() - timedelta(days=1):
				existing.start_time = st
				existing.end_time = et
				existing.expiration = expiration
				session.commit()
				status = True
			else:
				status = False
		else:
			# If the activity doesn't exist in the database, adds it.
			new = Activity(activity_id=act_id, start_time=st, end_time=et,
				expiration=expiration, user=user)
			session.add(new)
			session.commit()
			status = True

	return status

def extract_params(activity):
	"""
	Given a JSON activity object from WEconnect, extract the important
	parameters (start time, end time, and expiration date).

	:param dict activity: an activity from WEconnect in JSON format
	"""
	# Determines the start and end times
	ts = datetime.strptime(activity["dateStart"], WC_FORMAT)
	te = ts + timedelta(minutes=activity["duration"])

	# Determines the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if activity["repeat"] == "never":
		expiration = te
	if activity["repeatEnd"] != None:
		expiration = datetime.strptime(activity["repeatEnd"], WC_FORMAT)

	return ts, te, expiration

def get_users_with_current_activities(session):
	"""
	Get a list of all the users who have activities starting or ending within
	the next 15 minutes.

	:param sqlalchemy.orm.session.Session session: the database session
	"""
	users = []
	now = datetime.now().time()
	margin = timedelta(minutes=15)
	activities = session.query(Activity).all()
	for activity in activities:
		st = activity.start_time
		et = activity.end_time
		if (st - margin).time() <= now and now <= (et + margin).time():
			print(activity.user)
			if not activity.user in users:
				users.append(activity.user)
	return users

def get_yesterdays_progress(session, user):
	"""
	Get the daily_progress component from yesterday's last log.

	:param sqlalchemy.orm.session.Session session: the database session\n
	:param background.models.User user: the user for which to get progress
	"""
	yesterdays_logs = []
	yesterday = datetime.now() - timedelta(days=1)
	start = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0)
	end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59)
	yest_log = user.logs.filter(Log.timestamp > start, Log.timestamp < end).\
		order_by(Log.timestamp.desc()).first()
	return yest_log.daily_progress