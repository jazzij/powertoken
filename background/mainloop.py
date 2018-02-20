import dbmanager
import weconnect, fitbit

STEP_GOAL = 1000000

def setup():
	pt_users = dbmanager.get_users()
	for user in pt_users:
		fb = fitbit.Fitbit(user["fb_token"], user["goal_period"])
		fb.change_step_goal(STEP_GOAL)

def loop():
	"""
	This code will run forever.
	"""
	while True:
		pt_users = dbmanager.get_users()
		for user in pt_users:
			pollAndUpdate(user)

def pollAndUpdate(user):
	# Sets up the objects that will perform the WEconnect and Fitbit API
	# calls
	user_id = user["id"]
	wc = weconnect.WeConnect(user["wc_id"], user["wc_token"], user["goal_period"])
	fb = fitbit.Fitbit(user["fb_token"], user["goal_period"])

	# Polls WEconnect for changes and then updates Fitbit. Progress will be a 
	# decimal percentage.
	progress = wc.poll()

	# Makes sure the poll request succeeded
	if progress != -1:
		step_count = fb.reset_and_update(progress)
		dbmanager.add_log(user_id, progress, step_count)