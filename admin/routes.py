# admin.py

import math
from flask import Flask, json, redirect, render_template, request, url_for
import admin
from ptmodels import PtLog, PtUser

# Creates a new Flask server application
app = Flask(__name__)

# The dashboard
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
	pt_users = admin.load_users()
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