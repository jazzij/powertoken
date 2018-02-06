from tinydb import TinyDB

class PtUser:
	def __init__(self, username, registered_on, wc_login_status, fb_login_status, logs=PtLog[]):
		self.username = username
		self.registered_on = registered_on
		self.wc_login_status = wc_login_status
		self.fb_login_status = fb_login_status
		self.logs = logs

	def most_recent_wc():
		wc_daily = self.logs[len(logs) - 1].wc_daily_progress
		wc_weekly = self.logs[len(logs) -1].wc_weekly_progress
		return wc_daily, wc_weekly

	def most_recent_fb():
		fb_daily = self.logs[len(logs) - 1].fb_daily_count
		fb_weekly = self.logs[len(logs) -1].fb_weekly_count
		return fb_daily, fb_weekly

class PtLog:
	def __init__(self, username, wc_daily_progress, wc_weekly_progress, fb_daily_count, fb_weekly_count):
		self.username = username
		self.wc_daily_progress = wc_daily_progress
		self.wc_weekly_progress = wc_weekly_progress
		self.fb_daily_count = fb_daily_count
		self.fb_weekly_count = fb_weekly_count