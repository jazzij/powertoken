# admin.py

import math
from flask import Flask, json, redirect, render_template, request, url_for
import dbmanager
from ptmodels import PtLog, PtUser

# Creates a new Flask server application
app = Flask(__name__)

# The dashboard
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
	pt_users_raw = dbmanager.get_users()
	pt_users = []
	for user_raw in pt_users_raw:
		id = user_raw["id"]
		username = user_raw["username"]
		registered_on = user_raw["registered_on"]
		goal_period = user_raw["goal_period"]
		wc_status = "Current" if (user_raw["wc_id"] and user_raw["wc_token"]) else "Expired"
		fb_status = "Current" if user_raw["fb_token"] else "Expired"
		user = PtUser(id, username, registered_on, goal_period, wc_status, wc_status)
		logs_raw = dbmanager.get_logs(id)
		last_progress = logs_raw[len(logs_raw) - 1]["wc_progress"]
		user.wc_daily_progress = math.floor(last_progress * 100)
		pt_users.append(user)
	return render_template("home.html", pt_users=pt_users)
	
@app.route("/manage")
def manage():
	'''
	pt_users = [
		PtUser("Norbert", "01-27-2018 08:30:00", "Current", "Current"),
		PtUser("DaraS", "01-27-2018 08:40:00", "Current", "Expired")
	]
	'''
	return render_template("manage.html", pt_users=pt_users)
	
@app.route("/stats")
def stats():
	dbm = dbmanager.DbManager()
	pt_stats = dbm.load_logs()
	return render_template("stats.html", pt_stats=pt_stats)
	
@app.route("/docs")
def docs():
	return render_template("docs.html")
	
if __name__ == "__main__":
	app.run(debug=True)