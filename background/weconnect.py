"""
SUPPORT automated polling to/from WeCONNECT API for regular updates
Within background model 

Contributors: Abigail Franz, Sunny Parawala, Jasmine Jones
Last Update: March 2019

Using event listeners may prove to be useful: https://docs.sqlalchemy.org/en/latest/core/event.html

"""
from datetime import datetime, MAXYEAR, timedelta
import json, logging, requests
from database import User, Activity, Event, Error
from sqlalchemy import event

@event.listens_for(Event.completed, 'set')
def append_listener(target, value, old_value, initiator):
	#fitbit.update_progress_decimal(user, progress)
	print("modified")
	

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


#CONSTANTS
WC_URL = "https://palalinq.herokuapp.com/api/People"
WC_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)

DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
BASE_URL = "https://palalinq.herokuapp.com/api/people"



''' 
FLOW: 
1. GET NEW ACTIVITIES: For each user, check if any saved activities (in db) are expired, 
	and check if WC API has any new activities for that user to add to db. Only runs at most 1nce per day
2. GET ACTIVITY EVENTS: In a time period, for all users in the db, get all events scheduled for that day
3. CHECK EVENT CHECKIN: In a time period, for all users in the db, check WC API for checkins and update DB*

**ADD EVENT HANDLER to CHECK EVENT CHECKIN to trigger Fitbit script to run on any updates to the db   
'''

def get_activity_info(user, session):
	url = "{}/{}/activities?access_token={}".format(BASE_URL, user.wc_id,
			user.wc_token)
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	else:
		error_msg = response.text
		error = Error(
			summary = "Couldn't get list of activities.",
			origin = "background/weconnect.py, in _get_activities",
			message = error_msg,
			user = user
		)
		session.add(error)
		session.commit()
		return None    	

def get_todays_events(user, session):
	today = datetime.now()
	st = today.strftime("%Y-%m-%dT00:00:00")
	et = today.strftime("%Y-%m-%dT23:59:59")
	
	response = requests.get(WC_URL+"/"+str(user.wc_id)+"/activities-with-events",params={"access_token":user.wc_token,"from":st,"to":et})

	if response.status_code != 200:
		logging.debug("Couldn't get activities with events for {}".format(today))
		error_msg = response.text
		error = Error(
			summary = "Couldn't get activities with events for {}".format(today),
			origin = "background/wc_poll.py, in get_todays_events",
			message = error_msg,
			user = user)
		session.add(error)
		try:
			session.commit()
		except:
			logging.debug("Error in commiting Error to DB")
		finally:
			return []

	#RESPONSE is GOOD
	activity_events = response.json()
	return activity_events

		

def update_db_events(activity_events, session):
	'''
	@params: json activity-events from WeConnect,  sqlalchemy session
	@return: number of completed checkins detected, total events counted
	'''
	checkins = 0
	event_ids = []
	for activity in activity_events:
		wc_act_id = activity["activityId"]
		if pt_activityExists(wc_act_id, session): #ignore activities that were added that day
			eid = activity["events"][0]["eid"]
			event = session.query(Event).filter_by(eid=eid).first()
			if event is not None:
				checkin_val = activity["events"][0]["didCheckin"]
				if not event.completed:
					event.completed = checkin_val
				if checkin_val: checkins+=1
				event_ids.append(event.eid)
				logging.debug("{} completed? {}".format(event.eid, event.completed))
	logging.debug("{} checkins logged.".format(checkins))
	session.commit()
	return checkins, event_ids
	
def add_events_to_db(activity_events, session):
	'''
	@param list of activity_event json from weconnect
	'''
	parsedEvents = []
	
	#add events to DB for each of the user's activities
	for activity in activity_events:
		wc_act_id = activity["activityId"]
		if not pt_activityExists(wc_act_id, session):
			logging.debug("creating new activity {}".format(wc_act_id))
			create_new_activity(activity, session)
			    	
		for event in activity["events"]:
			newEv = create_new_event(event)
			print(newEv)
			parsedEvents.append(newEv)    
			if not pt_eventExists(newEv.eid, session):
				session.add(newEv)
	session.commit()
	return parsedEvents
	

def create_new_event(json_event):
	'''
	#helper function to convert json values to proper Db model values
	@param: json_event (from Weconnect). event = {eid, dateStart, activitity_id, didCheckin}
	'''
	startTime = datetime.strptime(json_event["dateStart"], WC_DATE_FMT)
	duration = timedelta(minutes=int(json_event["duration"]))
	endTime = startTime+duration
	newEvent = Event(eid=json_event["eid"], start_time=startTime, end_time=endTime, activity_id=json_event["activityId"], completed=(json_event["didCheckin"] is True))
	return newEvent


def pt_eventExists(eid, session):
	ev = session.query(Event).filter_by(eid=eid).first()
	if ev is None:
		logging.debug("Event with id:{} does not exist".format(eid))
		return False
	else:
		logging.debug("Found event with id:{}".format(eid))
		return True

def pt_activityExists(act_id, session):
	act = session.query(Activity).filter_by(wc_act_id=act_id).first()
	if act is None:
		return False
	else:
		return True
     	
def create_new_activity(activity, session):
	'''
	Creates a new activity for user from given json, with default weight of 3
	@param: activity (json), session (sqlalchemy)
	@return: Activity object
	'''
	act_dict = wc_json_to_db(activity)
	newAct = Activity(wc_act_id=act_dict["wc_act_id"], name=act_dict["name"], expiration=act_dict["expiration"], user_id=act_dict["user_id"])
	session.add(newAct)
	#logging.debug("Created activity {}".format(act_dict))

	try:
		session.commit()
	except:
		session.rollback()
		logging.error("Session commit failed for {}".format(act_dict["wc_act_id"]))
	finally:
		return

def wc_create_new_user(email, pw, phone, session):
	params = {"email":email, 
		"password":pw, 
		"firstName":"pt", 
		"lastName":"user", 
		"gender":"male", 
		"birthday":"1990-01-01", 
		"soberday":"2019-06-18", 
		"phone": phone
		}
	
	response = requests.post(WC_URL, data=params)
	if response.status_code == 200:
		return response.json()
	else:
		logging.error("Could not create new user. Response code {}, text".format(response.status_code, response.text))
	
	
	
			
#HELPER FUNCTION FOR SAVE NEW ACTIVITIES (duplicated from powertoken/api_util.py)
def wc_json_to_db(wc_act):
	"""
	Given a JSON activity object from WEconnect, convert it to an activity dict
	object compatible with the database.

	:param dict wc_act: an activity from WEconnect in JSON format
	return activity{ id, name, expiration, user=None}
	"""
	# Determine the start and end times
	ts = datetime.strptime(wc_act["dateStart"], WC_DATE_FMT)
	te = ts + timedelta(minutes=wc_act["duration"])

	# Determine the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if wc_act["repeat"] == "never":
		expiration = te
	if wc_act["repeatEnd"] != None:
		expiration = datetime.strptime(wc_act["repeatEnd"], WC_DATE_FMT)
	
	activity = {}
	activity["wc_act_id"] = wc_act["activityId"]
	activity["name"] = wc_act["name"]
	activity["expiration"] = expiration
	activity["user_id"] = wc_act["userId"]

	return activity


def get_events_for_user( user, session, onDate=None):
	if onDate is None:
		onDate = datetime.now()
	
	#Query user's activities that have not expired, and retrieve events from those activities
	acts = user.activities.filter(Activity.expiration > datetime.now()).all()
	logging.debug("Today's events for {}:".format(user.username))
	today_events = []
	for a in acts:
		ev = a.events.filter(Event.start_time >= onDate.date()).first()
		if ev is not None: 
			today_events.append(ev)
	logging.debug("(GET EVENTS FOR USER): {}".format(today_events))	
	
	for ev in today_events:
		logging.debug("Ev {} checked in? {}".format(ev.activity.name, ev.completed))
	
	return today_events
		
			

def calculate_percentageComplete(user, session):
	'''
	1. From DB - Events for TODAY from USER
	2. Count CHECKIN's
	3. COMPLETE #CHECKIN / #EVENTS
	4. Return COMPLETE as DECIMAL
	'''
	pass
	events = get_events_for_user(user, session)
	count = 0
	for ev in events:
		if ev.completed:
			count += 1
	
	return count / len(events)
	return percentage
	

def calculate_tallyComplete(user, session, fromDate=datetime.now().date()):
	'''
	1. Get all Users' Events from given DATE that were marked Completed 
	2. Add up the number of events
	@param fromDate default TODAY
	'''
	pass
	
def calculate_weightComplete(fromDate=datetime.now().date()):
	pass


###
### SCRIPT TO RUN
###
if __name__ == "__main__":
	from database import get_session, close_connection
	db_session = get_session()
	all_evs = db_session.query(Event).all()
	all_evs[-1].start_time = datetime.now()
	db_session.commit()
	
	print("Completed poll") 
	close_connection()
'''
	try:
		all_users = db_session.query(User).all()
		for user in all_users:
			logging.info("Polling {}".format(user.username))
			if user.wc_id and user.wc_token:	
				#activity_info = get_activity_info(user, db_session)
				#print(activity_info)
				evs = get_todays_events(user, db_session) or []
				update_db_events(evs, db_session)
				logging.info("Found {} events for user {}".format(len(evs), user.wc_id))
			else:
				logging.info("User {} has insufficient info".format(user.username))
	finally:
		db_session.close()
'''
