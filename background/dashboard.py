from database import get_session, User, Day, Activity, Event
from database import clear_db
from fitbit import DEFAULT_GOAL as goal, get_dashboard_state, clear_user_log, log_step_activity
from weconnect import get_events_for_user
import sys


def change_steps(user, target_steps, session):
	day = user.thisday()
	
	#change step count in fitbit
	#diff = target_steps - day.computed_progress
	#update = update_progress_count(user, diff, session)
	clear_user_log(user, session)
	update = log_step_activity(user, target_steps, session)
	print("Updated steps to {}".format(update))
	#change step count in day
	day.computed_progress = update
	session.commit()

def change_metaphor(username, metaphor, session):
	user = session.query(User).filter_by(username=username).first()
	if user:
		user.metaphor = metaphor
		print("UPDATE: {} metaphor changed to {}".format(user.username, user.metaphor))
		session.commit()
	else:
		print("No user {} found".format(name))


if __name__ == "__main__":
	'''
	args. Opt 1: dashboard.py -m username metaphor
	'''	
	session = get_session()

	if len(sys.argv) > 1:
		if sys.argv[1] == "-m":
			#CHANGE METAPHOR for USER
			name = sys.argv[2]
			metaphor = sys.argv[3]
			change_metaphor( name, metaphor, session)
		elif sys.argv[1] == "-d":
			# DELETE USER FROM DATABASE
			name = sys.argv[2]	
			clear_db(name, session)
		elif sys.argv[1] == "-l":
			name = sys.argv[2]
			step_count = int(sys.argv[3])
			user = session.query(User).filter_by(username=name).first()
			change_steps( user, step_count, session)
			#get_dashboard_state(user)
	else:		
		users = session.query(User).all()
		for user in users:
			events = get_events_for_user(user, session)
			print("{}'s metaphor: {}".format(user.username, user.metaphor))
			for ev in events:
				act = ev.activity
				print("{} weight:{}, completed: {}".format(act.name, act.weight, ev.completed ))

			today = user.thisday()
			if today is not None:
				print("User's day-- count: {}, progress:{}, Goal:{}".format(today.complete_count, today.computed_progress, goal))
				print("User sees on Fitbit: ")
			print(get_dashboard_state(user))
	

