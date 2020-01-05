import sys
from datetime import datetime
from database import db_session
from data.models import User, Activity, Event, Error, Log
from fitbit import get_dashboard_state
#import background.weconnect as weconnect


'''
PEEK allows a user to quickly look at the state of dynamic DB variables
USERS
EVENTS

and check to make sure API states match this database state
'''
users = []
if len(sys.argv) == 1:
	users = db_session.query(User).all()
else:
	print(sys.argv[1])
	users.append( db_session.query(User).filter_by(username=str(sys.argv[1])).first() )

#CHECK 1:
print ( users )

#CHECK 2: Print logged events for each user
#-- get all events for TODAY, with ACT_ID X, belonging to user U
# acts = user.activities.filter(Activity.expiration < datetime.now()).all()
# acts2 = db_session.query(Activity).filter(Activity.expiration < datetime.now(), Activity.user_id == user.wc_id).all()

for user in users:
	acts = user.activities.filter(Activity.expiration > datetime.now()).all()
	print("For {}...".format(user.username))
	today_events = []
	for a in acts:
		#print("{} {}".format(a.name, a.events.all()))
		ev = a.events.filter(Event.start_time >= datetime.now().date()).first()
		if ev is not None: 
			today_events.append(ev)
	print(today_events)	
	for ev in today_events:
		print("Ev {} checked in? {}".format(ev.activity.name, ev.completed))
	
	fb_state = get_dashboard_state(user)
	print("User {} sees: {} steps".format(user.username, fb_state))



