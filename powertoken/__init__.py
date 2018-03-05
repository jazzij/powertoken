# __init__.py
# Python Flask main application. Handles form processing and routing.
# To run this application, type "python __init__.py" at the command line.
# Created by Jasmine Jones
# Last modified by Abigail Franz on 2/21/2018

import os, requests
from flask import Flask, json, redirect, render_template, request, url_for
from flask.sessions import SecureCookieSession
import login, admin

# Creates a new Flask server application
app = Flask(__name__)
print("Just created a new Flask server app")

# We will use the Login object to access the PowerToken login functionality
login = login.Login()
print("Just created a new Login object")

session = SecureCookieSession()
session.permanent = True
session.modified = True
print("Just created a new SecureCookieSession object")

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
	print("A browser requested the homepage")
	if not session.get("username"):
		return redirect(url_for("pt_login"))
	else:
		return render_template("main/home.html", username=session["username"])

@app.route("/pt_login", methods=["GET", "POST"])
def pt_login():
	# GET: renders the PowerToken login page
	if request.method == "GET":
		print("A browser requested the pt_login.html file")
		return render_template("main/pt_login.html")

	# POST: processes the PowerToken login form
	elif request.method == "POST":
		print("A client submitted the pt_login form")
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
		print("A browser requested the wc_login.html file")
		return render_template("main/wc_login.html")

	# POST: processes the WEconnect login form
	elif request.method == "POST":
		print("A client submitted the wc_login form")
		# Logs user into WEconnect
		email = request.form["email"]
		password = request.form["password"]
		goal_period = request.form["goalPeriod"]
		login_successful = login.login_to_wc(session.get("username"), email, 
				password, goal_period)

		# If the login failed, reloads the page with an error message
		if not login_successful:
			error_message = "Login failed. Try again."
			return render_template("main/wc_login.html", login_error=error_message)

		# Redirects to Fitbit login page
		return redirect(url_for("fb_login"))

@app.route("/fb_login", methods=["GET", "POST"])
def fb_login():
	# GET: renders the Fitbit login page
	if request.method == "GET":
		print("A browser requested the fb_login.html page")
		return render_template("main/fb_login.html")

	# When Fitbit is all setup, fb_login.js redirects here.
	elif request.method == "POST":
		print("A client submitted the fb_login form")
		# Converts the response into the correct format and passes it to a function
		# that stores the user's access token in the database
		data = request.data
		conv_data = data.decode('utf8')
		datajs = json.loads(conv_data)
		login.complete_fb_login(session.get("username"), datajs["tok"])

		# This code will never be called but must be present
		return render_template("main/home.html")

@app.route("/admin")
@app.route("/admin/home")
@app.route("/admin/index")
@app.route("/admin/default")
def admin():
	# Gets the admin page
	admin = admin.PtAdmin()
	return render_template("admin/home.html", pt_users=admin.pt_users)

# In production, debug will probably be set to False.
if __name__ == "__main__":
	print("Running the Flask app")
	app.secret_key = os.urandom(12)
	app.run(threaded=True, debug=True)
