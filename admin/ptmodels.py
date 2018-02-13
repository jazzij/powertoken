class PtUser:
	def __init__(self, id, username, registered_on, goal_period, wc_id, wc_token, fb_token):
		self.id = id
		self.username = username
		self.registered_on = registered_on
		self.goal_period = goal_period
		self.wc_login_status = wc_login_status
		self.fb_login_status = fb_login_status

class PtLog:
	def __init__(self, id, user_id, timestamp, wc_progress, fb_step_count):
		self.id = id
		self.user_id = user_id
		self.timestamp = timestamp
		self.wc_progress = wc_progress
		self.fb_step_count = fb_step_count