from database import get_session, User, Day, Activity, Event
from fitbit import get_dashboard_state
from weconnect import get_events_for_user

session = get_session()
users = session.query(User).all()

for user in users:
	events = get_events_for_user(user, session)
	print("{}'s metaphor: {}".format(user.username, user.metaphor))
	for ev in events:
		act = ev.activity
		print("{} weight:{}, completed: {}".format(act.name, act.weight, ev.completed ))

	today = user.thisday()
	if today is not None:
		print("User's day-- count: {}, progress:{}".format(today.complete_count, today.computed_progress))
		print("User sees on Fitbit: ")
	print( get_dashboard_state(user))


