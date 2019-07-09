"""
Handles routing and form processing for the PowerToken Flask app.\n
Created by Jasmine Jones in 11/2017.\n
Modified by Abigail Franz, J. Jones. Last on July 2019.
"""
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

from datetime import datetime
import json
from flask import redirect, render_template, request, url_for
from werkzeug.urls import url_parse
from werkzeug.datastructures import MultiDict

from powertoken import app
import powertoken.db_util as db_util
import powertoken.api_util as api_util 

from powertoken.forms import UserLoginForm, UserWcLoginForm, UserActivityForm


@app.route("/createDB")
def create_db():
	from powertoken import db
	db.create_all()
	return render_template("user_home.html", username="db")

@app.route("/")
@app.route("/index")
@app.route("/home")
def user_home():
	#return  "Hello worlds!"
	username = request.args.get("username") # or "TEST"

	# If the user isn't logged in, redirect to the PowerToken login.
	if username is None:
		return redirect(url_for("user_login"))

	# If the user is logged in, show the welcome page.
	return render_template("user_home.html", username=username)

@app.route("/info")
def study_info():
	return render_template("study_info.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
	form = UserLoginForm()

	#POST ...
	if form.validate_on_submit():
		username = form.username.data

		#if user not in database, add new user
		if not db_util.pt_userExists(username):
			db_util.pt_addUser(username)

		#user is in database, but tokens are missing, redirect to login
		if not db_util.pt_userProfileComplete(username):
			return redirect(url_for("user_wc_login", username=username))

		#user exists with all API info intact, bypass login
		return render_template("user_home.html", username=username)


	# GET: Render the PowerToken login page.
	error = request.args.get("error")
	if error:
		return render_template("user_login.html", form=form, error=error)
	else:
		return render_template("user_login.html", form=form)

@app.route("/user_wc_login", methods=["GET", "POST"])
def user_wc_login():
	form = UserWcLoginForm()

	# POST: Process the WEconnect login form.
	if form.validate_on_submit():
		username = request.args.get("username")

		# If for whatever reason the username wasn't saved, return to the
		# original PowerToken login page.
		if username is None:
			return redirect(url_for("user_login", error="Invalid username"))

		# Get the user with that username from the database. go back to login page if
		# invalid user. This shouldn't happen but just in case.
		if not db_util.pt_userExists(username):
			return redirect(url_for("user_login", error="Invalid user"))

		# If everything is okay so far, get WEconnect info from the form and
		# login to external WEconnect server.
		email = form.email.data
		password = form.password.data
		success, result = api_util.login_to_wc(email, password)

		# If the username or password is incorrect, prompt the user to re-enter
		# credentials.
		if not success:
			error = "Incorrect username or password"
			return render_template("user_wc_login.html", form=form, error=error)

		# If the login was successful, store the WEconnect ID and access token
		# in the database, pull the user's WEconnect activities into the
		# database, and redirect to the Fitbit login.
		wc_id = result[0]
		wc_token = result[1]

		activities = api_util.get_wc_activities(wc_id, wc_token)
		errormsg = db_util.wc_addInfo(username, wc_id, wc_token, activities)

		if errormsg is None:
			logging.info("Added User Info for {}:{}".format(username, wc_id))
		else:
			return render_template("user_wc_login.html", form=form, error=errormsg)

		#TODO: change order of execution to get weights added here, before FB login.

		#Get Fitbit Token
		return redirect(url_for("user_fb_login", username=username))

	# GET: Render the WEconnect login page.
	return render_template("user_wc_login.html", form=form)



@app.route("/user_fb_login", methods=["GET", "POST"])
def user_fb_login():
	'''
	fyi production callback url: https://powertoken.grouplens.org/fb_login
	test callback url: http://localhost:5000/user_fb_login
	'''
	# POST: Process response from external Fitbit server.
	username = request.args.get("username")
	#return render_template("user_home.html", username=username)

	if request.method == "POST":
		# Extract the Fitbit token and username from the response data.
		fb_token, username = api_util.complete_fb_login(request.data)

		# If the username wasn't saved, return to the original PowerToken login
		# page.
		logging.debug("POST for Username {}".format(username))
		if username is None:
			return redirect(url_for("user_login", error="No username given"))

		# Get the user with that username from the database. go back to login page if
		# invalid user. This shouldn't happen but just in case.
		if not db_util.pt_userExists(username):
			return redirect(url_for("user_login", error="Invalid username. Please create user profile"))

		#ADD INFO TO DB
		db_util.fb_addInfo(username, fb_token)
		
		#UPDATE USERS STEP GOAL IN FITBIT
		api_util.fb_updateUserGoal(fb_token)

		return render_template("user_home.html", username=username)

	# GET: Render Fitbit page, which redirects to external login.
	elif request.method == "GET":
		username = request.args.get("username")
		return render_template("user_fb_login.html", username=username)


@app.route("/user_activities", methods=["GET", "POST"])
def user_activities():
	''' NOTE: This function is called via js redirect from user_fb_login.html'''
	username = request.args.get("username")

	# If for whatever reason the username wasn't saved, go back to the
	# original login screen.
	if username is None:
		return redirect(url_for("user_login", error="Invalid username"))

	if not db_util.pt_userExists(username):
		return redirect(url_for("user_login", error="Invalid username"))

	form = UserActivityForm()

	# GET: Set up the form for activity weighting and render the page.
	if request.method == "GET":
		activities = db_util.wc_getUserActivities(username)	#returns list of MultiDict
		for a in activities:
			form.activities.append_entry(data=a)
		return render_template("user_activities.html", form=form)

	# POST: Process the submitted activity weighting form.
	elif request.method == "POST":
		logging.debug(form.activities.entries)
		act_weights = []
		for entry in form.activities.entries:
			# Strip '[' and ']' characters added by MultiDict representation
			entry_id = entry.wc_act_id.data[1:-1]
			#create and send a tuple of wc_act_id, weight
			act_weights.append((entry_id, entry.weight.data))

		db_util.wc_addActivityWeight(username, act_weights)
		return redirect(url_for("user_home", username=username))

	'''
	user = User.query.filter_by(username=username).first()
	form = UserActivityForm()

	# POST: Process the submitted activity weighting form.
	if request.method == "POST":
		for entry in form.activities.entries:
			# Strip '[' and ']' characters added by MultiDict representation
			entry_id = entry.wc_act_id.data[1:-1]
			activity = user.activities.filter_by(wc_act_id=entry_id).first()
			activity.weight = entry.weight.data
		db.session.commit()
		return redirect(url_for("user_home", username=username))
	'''

	# GET: Set up the form for activity weighting and render the page.
'''	elif request.method == "GET":
		for act in user.activities.all():
			# Don't show the user expired activities (but they still need to be
			# in the database).
			if act.expiration < datetime.now():
				continue

			# The append_entry method only takes a MultiDict data structure.
			d = MultiDict([("wc_act_id", act.wc_act_id), ("act_name", act.name),
					("weight", act.weight)])
			form.activities.append_entry(data=d)
		return render_template("user_activities.html", form=form)'''


@app.teardown_appcontext
def shutdown_session(exception=None):
	db_util.close_session()
	

# define the visualization related stuff here
@app.route("/overview/<name>")
def user_overview(name):
	dict = db_util.viz_dataDict(name)
	return render_template("overview_viz.html", activity_data= dict)	
	
	
@app.route("/practice/<name>")
def practice(name):

	#username = request.args.get("username")
	username = name
	dict = db_util.viz_dataDict(name)
	
	
	return render_template("overview_viz.html", activity_data= dict)
