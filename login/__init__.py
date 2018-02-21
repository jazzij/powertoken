# __init__.py
# Python Flask main application. Handles form processing and routing.
# To run this application, type "python __init__.py" at the command line.
# Created by Jasmine Jones
# Last modified by Abigail Franz on 2/21/2018

import os, requests
from flask import Flask, json, redirect, render_template, request, url_for
from flask.sessions import SecureCookieSession
import login

# Creates a new Flask server application
app = Flask(__name__)

# We will use the Login object to access the PowerToken login functionality
login = login.Login()

session = SecureCookieSession()
session.permanent = True
session.modified = True

@app.before_request
def session_management():
	session.permanent = True
	session.modified = True

# The landing page
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
	if not session.get("username"):
		return redirect(url_for("pt_login"))
	else:
		return render_template("home.html", username=session["username"])

@app.route("/pt_login", methods=["GET", "POST"])
def pt_login():
	# GET: renders the PowerToken login page
	if request.method == "GET":
		return render_template("pt_login.html")

	# POST: processes the PowerToken login form
	elif request.method == "POST":
		session["username"] = request.form["username"]
		session.modified = True

		# Checks if the user already exists in the database
		if login.is_current_user(session.get("username")):

			# If the user is already logged into WEconnect and Fitbit, he/she is
			# redirected to the home page
			if (login.is_logged_into_wc(session.get("username")) and 
				login.is_logged_into_fb(session.get("username"))):
				return redirect(url_for("home"))

			# Otherwise, the user is sent right to the WEconnect login
			else:
				return redirect(url_for("wc_login"))

		# If this is a new user, adds him/her to the database and redirects to
		# the WEconnect login
		else:
			login.create_user(session.get("username"))
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
		login_successful = login.login_to_wc(session.get("username"), email, 
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
		# that stores the user's access token in the database
		data = request.data
		conv_data = data.decode('utf8')
		datajs = json.loads(conv_data)
		login.complete_fb_login(session.get("username"), datajs["tok"])

		# This code will never be called but must be present
		return render_template("home.html")

"""Shoudn't be needed anymore.
@app.route("/start", methods=["GET"])
def start():
	# Start page redirects to the /running route, but running.html is the
	# document that is displayed
	return render_template("running.html")

@app.route("/running", methods=["GET"])
def running():
	# Begins the program loop, which will run until killed
	powertoken.start_experiment(session.get("username"))

	# This code will never be called
	return render_template("home.html")
"""

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(threaded=True, debug=True)