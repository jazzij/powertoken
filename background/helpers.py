"""
Contains some helper functions for the background scripts.\n
Created by Abigail Franz on 3/16/2018.\n
Last modified by Abigail Franz on 3/26/2018.
"""

from datetime import datetime, timedelta, MAXYEAR
from db import session
from models import Activity, Day, Event, User
import weconnect

d = datetime.now()
today = datetime(d.year, d.month, d.day)

def add_or_update_activity(activity, user):
	"""
	Insert new activity row into the database if it doesn't already exist and
	is not expired. If it exists but has been updated, update it in the
	database. Return "Inserted" if activity was inserted, "Updated" if updated,
	and False if neither.

	:param sqlalchemy.orm.session.Session session: the database session\n
	:param dict activity: an activity from WEconnect in JSON format\n
	:param background.models.User user: the user to which the activity belongs
	"""
	# Determines the start and end times and expiration date (if any)
	st, et, expiration = extract_params(activity)
	act_id = activity["activityId"]

	# Flag indicating whether or not the activity was inserted/updated
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
			modified = datetime.strptime(activity["dateModified"], weconnect.DATE_FMT)
			if modified >= datetime.now() - timedelta(days=1):
				existing.start_time = st
				existing.end_time = et
				existing.expiration = expiration
				session.commit()
				status = "Updated"
			else:
				status = False
		else:
			# If the activity doesn't exist in the database, adds it.
			new = Activity(activity_id=act_id, start_time=st, end_time=et,
				expiration=expiration, user=user)
			session.add(new)
			session.commit()
			status = "Inserted"

	return status

def extract_params(activity):
	"""
	Given a JSON activity object from WEconnect, extract the important
	parameters (start time, end time, and expiration date).

	:param dict activity: an activity from WEconnect in JSON format
	"""
	# Determines the start and end times
	ts = datetime.strptime(activity["dateStart"], weconnect.DATE_FMT)
	te = ts + timedelta(minutes=activity["duration"])

	# Determines the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if activity["repeat"] == "never":
		expiration = te
	if activity["repeatEnd"] != None:
		expiration = datetime.strptime(activity["repeatEnd"], weconnect.DATE_FMT)

	return ts, te, expiration

def get_users_with_current_activities():
	"""
	Get a list of all the users who have activities starting or ending within
	the next 15 minutes.

	:param sqlalchemy.orm.session.Session session: the database session
	"""
	users_to_monitor = []
	now = datetime.now().time()
	margin = timedelta(minutes=15)
	users = session.query(User).all()
	for user in users:
		day = user.days.filter(Day.date == today)
		events = day.events.filter((Event.start_time - margin).time() <= now).\
				filter(now <= (Event.end_time + margin).time()).count()
		if events:
			users_to_monitor.append(user)
	return users_to_monitor

def get_yesterdays_progress(user):
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

def populate_todays_events(user):
	"""
	Populate the database with a list of the user's activity-events today.

	:param background.models.User user: the user for which to get events
	"""
	# Add a new Day to the user's days table if it doesn't already exist
	day = user.days.filter(Day.date == today).first()
	if day is None:
		day = Day(date=datetime(today.date, user=user))
		session.add(day)
		session.commit()

	# Get today's events from WEconnect and add them to the day's events table
	activity_events = weconnect.get_todays_events(user)
	for wc_act in activity_events:
		act = user.activities.filter(Activity.wc_act_id == wc_act["activityId"]).first()
		for wc_ev in wc_act["events"]:
			# If the event doesn't already exist for today, add it
			event = session.query(Event).filter(Event.eid == wc_ev["eid"]).first()
			if event:
				modified = datetime.strptime(wc_act["dateModified"], WC_FORMAT)
				if modified >= datetime.now() - timedelta(days=1):
					event.start_time = datetime.strptime(wc_ev["dateStart"], WC_FORMAT)
					event.end_time = act.start_time + timedelta(minutes=wc_ev["duration"])
					event.completed = wc_ev["didCheckin"]
			else:
				st = datetime.strptime(wc_ev["dateStart"], WC_FORMAT)
				et = start + timedelta(minutes=wc_ev["duration"])
				event = Event(eid=wc_ev["eid"], start_time=st, end_time=et,
						completed=wc_ev["didCheckin"], day=day, activity=act)
				session.add(event)
	session.commit()

def compute_possible_score(day):
    """
	Compute the highest possible score for a particular user on a particular
	day.

	:param background.models.Day day
	"""
    events = day.events.all()
    score = 0
    for ev in events:
        score += ev.activity.weight
    return score

def compute_days_progress(day):
	"""
	Compute the user's actual progress on a particular day.

	:param background.models.Day day
	"""
	score = 0
	day_0_acts = day.events.filter(Event.completed).all()
	for act in day_0_acts:
		score += event.activity.weight

	day_1_ago = day.user.days.filter_by(date=(day.date - timedelta(1))).first()
	day_1_acts = day_1_ago.events.filter(Event.completed).all()
	for act in day_1_acts:
		score += (act.activity.weight - 1)

	day_2_ago = day.user.days.filter_by(date=(day.date - timedelta(2))).first()
	day_2_acts = day_2_ago.events.filter(Event.completed).all()
	for act in day_2_acts:
		score += (act.activity.weight - 2) if act.activity.weight > 1 else 0

	day_3_ago = day.user.days.filter_by(date=(day.date - timedelta(3))).first()
	day_3_acts = day_3_ago.events.filter(Event.completed).all()
	for act in day_3_acts:
		score += (act.activity.weight - 3) if act.activity.weight > 2 else 0

	day_4_ago = day.user.days.filter_by(date=(day.date - timedelta(4))).first()
	day_4_acts = day_4_ago.events.filter(Event.completed).all()
	for act in day_4_ago.days_activities:
		score += (act.activity.weight - 4) if act.activity.weight > 3 else 0

	possible_score = compute_possible_score(day)
	return float(score) / float(possible_score)