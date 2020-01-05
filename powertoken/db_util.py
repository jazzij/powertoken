"""
DB UTIL
Abstract Database operations to support various Flask forms and views (routes.py)

For use with FLASK and SQLalchemy
Database schema / models - background.database
Database session object instantiated as part of Flask app (see __init__.py)

Last Update June 2019 by Jasmine Jones

"""
#from powertoken.models import User, Activity, Event
from background.database import User, Activity, Event, Day
from powertoken import db
from sqlalchemy import exc
from werkzeug.datastructures import MultiDict
import datetime
import logging, sys
import traceback

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def close_session():
	db.session.close()

def pt_userExists(username, db=db):
	''' RETURNS TRUE | FALSE '''
	user = db.session.query(User).filter_by(username=username).first()
	#user= User.query.filter_by(username=username).first()
	if user is None:
		return False
	else:
		return True

def pt_userProfileComplete(username, db=db):
	''' RETURNS TRUE | FALSE '''
	if pt_userExists(username, db):
		user= db.session.query(User).filter_by(username=username).first()
		if any ([not user.wc_id, not user.wc_token, not user.fb_token]):
			return False
		else:
			return True	
	else:
		return False

def pt_addUser(username, db=db):
	'''
	Given string @param username, adds a blank powertoken user with that name to the db 
	'''
	if pt_userExists(username, db):
		return
		
	user= User(username=username)
	user.metaphor = "tally"
	db.session.add(user)
	errorMsg = None
	
	#error when same name is added
	try:
		db.session.commit()
	except:
		db.session.rollback()
		logging.debug("User {} could not be added".format(username))	

	
def wc_addInfo(username, wc_id, wc_token, activities, db=db):
	'''
	Add wc_user id, token and related activity info from WC API call to the database
	@params username String, wc_id integer, wc_token string, activities Dict with keys=id,name,expiration
	'''

	#update user information, regardless of new user or not. tokens always refresh upon login	
	user = db.session.query(User).filter_by(username=username).first()
	user.wc_id = wc_id
	user.wc_token = wc_token
	
	#add and update new activities
	for act in activities:
		#check for existing ID
		old_activity = db.session.query(Activity).filter_by(wc_act_id=act["id"]).first()
		logging.debug("to addInfo, retrieved {}".format(old_activity))
		
		if old_activity is not None:
			#update existing activity (except key)
			old_activity.expiration = act["name"]
			old_activity.expiration = act["expiration"]
			user_id= wc_id
		else:
			#create new activity if none with ID found
			new_activity = Activity(wc_act_id=act["id"], name=act["name"], expiration=act["expiration"], user_id=wc_id)
			db.session.add(new_activity)

	#rollback session if commit fails
	errorMsg = None
	try:
		db.session.commit()
	except exc.IntegrityError as error:
		errorMsg = "Could not add user info to database"
		db.session.rollback()
		logging.debug(sys.exc_info()[0])
	finally:
		return errorMsg


def wc_getUserActivities(username, db=db):
	'''
	Get a list of a user's activities from the database
	Returns a MultiDict
	'''
	user = db.session.query(User).filter_by(username=username).first()
	if user is None:
		return None

	activities = []		
	for act in user.activities.all():
		# Don't show the user expired activities (but they still need to be
		# in the database).
		if act.expiration > datetime.datetime.now():
			# return a MultiDict data structure for use in flask forms
			d = MultiDict([("wc_act_id", act.wc_act_id), ("act_name", act.name),
					("weight", act.weight)])
			activities.append(d)
	
	return activities
	
def wc_addActivityWeight(username, activity_list, db=db):
	'''
	@params username string, activity_list is list of tuples [(id, weight), ...]
	'''
	user = db.session.query(User).filter_by(username=username).first()
	for act in activity_list:
		wc_act = user.activities.filter_by(wc_act_id=act[0]).first()
		wc_act.weight = act[1]

	db.session.commit()
	
def fb_addInfo(username, fb_token, db=db):
	'''
	Save fitbit token to user profile in the database
	@params powertoken username and fitbit token	
	'''
	user= db.session.query(User).filter_by(username=username).first()
	user.fb_token = fb_token
	
	errorMsg = None
	try:
		db.session.commit()
	except:
		db.rollback()
		errorMsg = "User with username already exists"

	return errorMsg

def viz_dataDict(username):
	'''
	Returns dict of data needed to generate vizualization
	'''
	# FORMAT	jstr = { "user": "PT002", "progress": 0.25, "activities": [{"start_time": "09:30:00", "weight": 5, "completed": "false", "name": "act1"}, {"start_time": "13:16:00", "weight": 3, "completed": "true", "name": "act2"}, {"start_time": "14:45:00", "weight": 1, "completed": "false", "name": "act3"}, {"start_time": "05:00:00", "weight": 2, "completed": "true", "name": "act4"}]}
	jstr = { "user": "test", "progress": 0.25, "activities": [{"start_time": "09:30:00", "weight": 5, "completed": "false", "name": "act1"}, {"start_time": "13:16:00", "weight": 3, "completed": "true", "name": "act2"}, {"start_time": "14:45:00", "weight": 1, "completed": "false", "name": "act3"}, {"start_time": "05:00:00", "weight": 2, "completed": "true", "name": "act4"}]}

	user = db.session.query(User).filter_by(username=username).first()
	if user is None:
		logging.info("User {} not found. Returning test data".format(username))
		return jstr
		
	user_name = user.username
	#from day get list of activities
	day = user.thisday() 
	if day is None:
		logging.info("User {} does not have this day. Returning test data".format(username))
		return jstr
		
	progress = day.computed_progress
	activities = [] #info: start_time, weight, name
	for event in day.events.all():
		time = event.start_time
		completed = event.completed
		name = event.activity.name
		weight = event.activity.weight
	
		activity = {"start_time": time, "weight": weight, "completed": completed, "name": name}
		activities.append(activity)
	
	# map charge/tally  step count to 0-1 scale
	if progress > 1	:
		progress = map_steps_to_progress(progress)
		logging.info("(db_util.viz_data) Steps to progress: {} to {}".format(day.computed_progress, progress))

	data = {"user":user_name, "progress":progress, "activities": activities}
	return data


def map_steps_to_progress(step_count):
	oldmin = 0
	oldmax = 100000
	newmin = 0
	newmax = 1
	
	oldrange = oldmax - oldmin
	newrange = newmax - newmin
	newvalue = (((step_count - oldmin) * newrange) / oldrange)  + newmin
	
	return newvalue











	