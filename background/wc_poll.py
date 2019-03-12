"""
SUPPORT automated polling to/from WeCONNECT API for regular updates
Within background model 

Contributors: Abigail Franz, Sunny, Jasmine Jones
Last Update: March 2019

Using event listeners may prove to be useful: https://docs.sqlalchemy.org/en/latest/core/event.html

"""
from datetime import datetime, MAXYEAR, timedelta
import json, logging, requests
from database import db_session
from data.models import User, Activity, Event, Error

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#CONSTANTS
WC_URL = "https://palalinq.herokuapp.com/api/People"
WC_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)

DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
BASE_URL = "https://palalinq.herokuapp.com/api/people"

''' FLOW: 
1. GET NEW ACTIVITIES: For each user, check if any saved activities (in db) are expired, 
	and check if WC API has any new activities for that user to add to db. Only runs at most 1nce per day
2. GET ACTIVITY EVENTS: In a time period, for all users in the db, get all events scheduled for that day
3. CHECK EVENT CHECKIN: In a time period, for all users in the db, check WC API for checkins and update DB*

**ADD EVENT HANDLER to CHECK EVENT CHECKIN to trigger Fitbit script to run on any updates to the db   
'''


#TODO GET WC ACTIVITIES
def get_activity_info(wc_id, wc_token):
	url = "{}/{}/activities?access_token={}".format(BASE_URL, user.wc_id,
			user.wc_token)
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	else:
		error = Error(
			summary = "Couldn't get list of activities.",
			origin = "background/weconnect.py, in _get_activities",
			message = response.json()["error"]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return []    	

#TODO GET WC EVENTS
def get_todays_events(wc_id, wc_token, session):
	today = datetime.now()
	st = today.strftime("%Y-%m-%dT00:00:00")
	et = today.strftime("%Y-%m-%dT23:59:59")
	response = requests.get(BASE_URL+"/"+str(wc_id)+"/activities-with-events",params={"access_token":wc_token,"from":st,"to":et})

	if response.status_code == 200:
		logging.debug(json.dumps(response.json(), indent=4))
		#return response.json()
	else:
		error = Error(
			summary = "Couldn't get activities with events for {}".format(today),
			origin = "background/wc_poll.py, in get_todays_events",
			message = response.json()["error"]["message"],
			user = wc_id
		)
		session.add(error)
		session.commit()
		return []
    
    #parse json response for events (SUNNY)
    activity_events = json.loads(response.json())
    for act, events in activity_events:
	#save_new_activities(activity_events, session)
    
    # save new events to DB
    save_new_events(activity_events)

#TODO SAVE WC ACTIVITES 
#def save_new_activities(activities, session):
#	for act in activities:
#		#search for wc_act_id in db
#		oldAct = session.query(Activity).filter_by(wc_act_id=act["activityId"]).first()	
#		if oldAct is None:
#			#convert json to activity object
#			newAct = wc_json_to_db(act)
#			session.add(Activity(wc_act_id=newAct["id"], name=newAct["name"], expiration=newAct["expiration"], user_id=wc_id))
			

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
	activity["id"] = wc_act["activityId"]
	activity["name"] = wc_act["name"]
	activity["expiration"] = expiration
	activity["user"] = None

	return activity



#TODO SAVE WC EVENTS

# TODO UPDATE WC EVENTS (check if checkin)

###
### SCRIPT TO RUN
if __name__ == "__main__":
	all_users = db_session.query(User).all()
	for user in all_users:
		logging.info("Polling {}".format(user.username))
		get_todays_events(user.wc_id, user.wc_token, db_session)
		db