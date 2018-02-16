# __init__.py
# Python Flask main application. Handles form processing and routing.
# To run this application, type "python routes.py" at the command line.
# Created by Jasmine Jones
# Last modified by Abigail Franz on 1/29/2018

import os, requests
from flask import Flask, json, redirect, render_template, request, session, url_for
from sqlalchemy import create_engine
import powertoken
import flaskmanager

# Creates a new Flask server application
app = Flask(__name__)
engine = create_engine(flaskmanager.engine_path, echo=True)

# We will use the powertoken object to access the core PowerToken functionality
powertoken = powertoken.PowerToken()

# The landing page
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
	#if session["username"]:
	#	return render_template("home.html", username=session["username"])
	#else:
	#	return render_template("home.html")
	if not session.get("username"):
		return redirect(url_for("pt_login"))
	else:
		return render_template("home.html")

@app.route("/pt_login", methods=["GET", "POST"])
def pt_login():
	# GET: renders the PowerToken login page
	if request.method == "GET":
		return render_template("pt_login.html")

	# POST: processes the PowerToken login form
	elif request.method == "POST":
		session["username"] = request.form["username"]

		# Checks if the user already exists in the TinyDB
		if powertoken.is_current_user(session["username"]):

			# If the user is already logged into WEconnect and Python, he/she is
			# redirected to the home page
			if (powertoken.is_logged_into_wc(session["username"]) and 
				powertoken.is_logged_into_fb(session["username"])):
				return redirect(url_for("home"))

			# Otherwise, the user is sent right to the WEconnect login
			else:
				return redirect(url_for("wc_login"))

		# If this is a new user, adds him/her to the TinyDB and redirects to the
		# WEconnect login
		else:
			powertoken.create_user(session["username"])
			return redirect(url_for("wc_login"))

@app.route("/wc_login", methods=["GET", "POST"])
def wc_login():
	# GET: renders the WEconnect login page
	if request.method == "GET":
		return render_template("wc_login.html")

	# POST: processes the WEconnect login form
	elif request.method == "POST":
		# Logs user into WEconnect
		email = request.form["email"]
		password = request.form["password"]
		goal_period = request.form["goalPeriod"]
		login_successful = powertoken.login_to_wc(session["username"], email, 
				password, goal_period)

		# If the login failed, reloads the page with an error message
		if not login_successful:
			error_message = "Login failed. Try again."
			return render_template("wc_login.html", login_error=error_message)

		# Redirects to Fitbit login page
		return redirect(url_for("fb_login"))

@app.route("/fb_login", methods=["GET", "POST"])
def fb_login():
	# GET: renders the Fitbit login page
	if request.method == "GET":
		return render_template("fb_login.html")

	# When Fitbit is all setup, fb_login.js redirects here.
	elif request.method == "POST":
		# Converts the response into the correct format and passes it to a function
		# that stores the user's access token in the TinyDB
		data = request.data
		conv_data = data.decode('utf8')
		datajs = json.loads(conv_data)
		powertoken.complete_fb_login(session["username"], datajs["tok"])

		# This code will never be called but must be present
		return render_template("home.html")

@app.route("/start", methods=["GET"])
def start():
	# Start page redirects to the /running route, but running.html is the
	# document that is displayed
	return render_template("running.html")

@app.route("/running", methods=["GET"])
def running():
	# Begins the program loop, which will run until killed
	powertoken.start_experiment(session["username"])

	# This code will never be called
	return render_template("home.html")

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(threaded=True, debug=True)