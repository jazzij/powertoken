# admin.py

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
		id = user_raw[0]
		username = user_raw[1]
		registered_on = user_raw[2]
		goal_period = user_raw[3]
		wc_status = "Current" if (user_raw[4] and user_raw[5]) else "Expired"
		fb_status = "Current" if user_raw[6] else "Expired"
		user = PtUser(id, username, registered_on, goal_period, wc_status, wc_status)
		logs_raw = dbmanager.get_logs(id)
		last_progress = logs_raw[len(logs_raw) - 1][3]
		user.wc_daily_progress = last_progress
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