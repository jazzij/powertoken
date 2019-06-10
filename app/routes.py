"""
Handles routing and form processing for the PowerToken Flask app.\n
Created by Jasmine Jones in 11/2017.\n
Last modified by Abigail Franz on 5/2/2018.
"""
import logging, sys

from datetime import datetime
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.datastructures import MultiDict
from app import app, db
from app.weconnect import check_wc_token_status, login_to_wc, set_wc_activities
from app.helpers import complete_fb_login
from app.forms import (AdminLoginForm, AdminRegistrationForm, UserLoginForm,
		UserWcLoginForm, UserActivityForm)
from app.models import Activity, Admin, Error, Log, User
from app.viewmodels import LogViewModel, UserViewModel, ActivityViewModel, EventLogViewModel

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

@app.route("/")
@app.route("/index")
@app.route("/home")
def user_home():
	username = request.args.get("username")

	# If the user isn't logged in, redirect to the PowerToken login.
	if username is None:
		return redirect(url_for("user_login"))

	# If the user is logged in, show the welcome page.
	else:
		return render_template("user_home.html", username=username)

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
	form = UserLoginForm()

	# POST: Process the PowerToken login form.
	if form.validate_on_submit():
		username = form.username.data
		user = User.query.filter_by(username=username).first()

		# If the user has not been added to the database, add the user to the
		# database and redirect to the WEconnect login.
		if user is None:
			user = User(username=username)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for("user_wc_login", username=username))


		# If the user exists in the database, but the WEconnect (or Fitbit)
		# info isn't filled out, redirect to the WEconnect login.
		if any([not user.wc_id, not user.wc_token, not user.fb_token]):
			return redirect(url_for("user_wc_login", username=username))

		#TODO Add token expiry check here
		# If user exists in the db, but token returns an error, then login again to refresh
		if not check_wc_token_status(user.wc_id, user.wc_token):
			return redirect(url_for("user_wc_login", username=username))


		# If the user exists in the database, and the WEconnect and Fitbit info
		# is already filled out, bypass the login process.
		return redirect(url_for("user_home", username=username))

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

		# Get the user with that username from the database.
		user = User.query.filter_by(username=username).first()
		priorUser = user is not None

		# If the user with that username isn't in the database for whatever
		# reason, go back to the PowerToken login page.
		if user is None:
			return redirect(url_for("user_login", error="Invalid user"))

		# If everything is okay so far, get WEconnect info from the form and
		# login to external WEconnect server.
		email = form.email.data
		password = form.password.data
		success, result = login_to_wc(email, password)

		# If the username or password is incorrect, prompt the user to re-enter
		# credentials.
		if not success:
			error = "Incorrect username or password"
			return render_template("user_wc_login.html", form=form, error=error)

		# If the login was successful, store the WEconnect ID and access token
		# in the database, pull the user's WEconnect activities into the
		# database, and redirect to the Fitbit login.
		user.wc_id = result[0]
		user.wc_token = result[1]
		logging.info("Adding User {}".format(user.wc_id))

		try:
			db.session.commit()
		except:
			error = "A user with the same WEconnect credentials already exists"
			return render_template("user_wc_login.html", form=form, error=error)

		#TODO: CHECK TO MAKE SURE THIS WORKS. only execute when there is an new user
		if not priorUser:
			set_wc_activities(user)
		return redirect(url_for("user_fb_login", username=username))

	# GET: Render the WEconnect login page.
	return render_template("user_wc_login.html", form=form)

@app.route("/user_fb_login", methods=["GET", "POST"])
def user_fb_login():
	# POST: Process response from external Fitbit server.
	if request.method == "POST":
		# Extract the Fitbit token and username from the response data.
		fb_token, username = complete_fb_login(request.data)

		# If the username wasn't saved, return to the original PowerToken login
		# page.
		if username is None:
			return redirect(url_for("user_login", error="Invalid username"))

		# Get the user with that username from the database.
		user = User.query.filter_by(username=username).first()

		# If the user with that username isn't in the database for whatever
		# reason, go back to the PowerToken login page.
		if user is None:
			return redirect(url_for("user_login", error="Invalid user"))

		# If everything is okay so far, add the Fitbit token to the database.
		user.fb_token = fb_token

		try:
			db.session.commit()
		except:
			db.rollback()

		# This code will never be called but must be present.
		return render_template("user_home.html", username=username)

	# GET: Render Fitbit page, which redirects to external login.
	elif request.method == "GET":
		username = request.args.get("username")
		return render_template("user_fb_login.html", username=username)

@app.route("/user_refresh", methods=["GET", "POST"])
def refresh_tokens():
	# GET PT USERNAME
	username = request.args.get("username")
	return redirect(url_for("user_wc_login", username=username))



@app.route("/user_activities", methods=["GET", "POST"])
def user_activities():
	username = request.args.get("username")

	# If for whatever reason the username wasn't saved, go back to the
	# original login screen.
	if username is None:
		return redirect(url_for("user_login", error="Invalid username"))

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

	# GET: Set up the form for activity weighting and render the page.
	elif request.method == "GET":
		for act in user.activities.all():
			# Don't show the user expired activities (but they still need to be
			# in the database).
			if act.expiration < datetime.now():
				continue

			# The append_entry method only takes a MultiDict data structure.
			d = MultiDict([("wc_act_id", act.wc_act_id), ("act_name", act.name),
					("weight", act.weight)])
			form.activities.append_entry(data=d)
		return render_template("user_activities.html", form=form)

# define the visualization related stuff here
@app.route("/user_overview")
def user_overview():
	return render_template("user_overview_viz.html")


"""
ADMIN
"""
@app.route("/admin")
@app.route("/admin/")
@app.route("/admin/index")
@app.route("/admin/home")
@login_required
def admin_home():
	'''
	Home: Display list of users with user data
	'''
	users = User.query.order_by(User.registered_on).all()
	user_vms = [UserViewModel(user) for user in users]
	return render_template("admin_home.html", user_vms=user_vms)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
	if current_user.is_authenticated:
		return redirect(url_for("admin_home"))
	form = AdminLoginForm()

	# POST: If a valid form was submitted
	if form.validate_on_submit():
		admin = Admin.query.filter_by(username=form.username.data).first()
		if admin is None or not admin.check_password(form.password.data):
			return redirect(url_for("admin_login", next=request.args.get("next")))
		login_user(admin, remember=False)
		next_page = request.args.get("next")
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for("admin_home")
		return redirect(next_page)

	# GET: Renders the admin login template.
	return render_template("admin_login.html", form=form)

@app.route("/admin/logout")
def admin_logout():
	logout_user()
	return redirect(url_for("admin_login"))

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
	# If a user who's already logged in tries to register, send him/her to the
	# homepage.
	if current_user.is_authenticated:
		return redirect(url_for("admin_home"))

	form = AdminRegistrationForm()

	# POST: Process the admin registration form.
	if form.validate_on_submit():
		admin = Admin(username=form.username.data, email=form.email.data)
		admin.set_password(form.password.data)
		db.session.add(admin)
		db.session.commit()
		login_user(admin, remember=False)
		next_page = request.args.get("next")
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for("admin_home")
		return redirect(next_page)

	# GET: Render the admin login page.
	return render_template("admin_register.html", form=form)

@app.route("/admin/progress_logs")
@login_required
def admin_progress_logs():
	logs = Log.query.order_by(Log.timestamp.desc()).all()
	log_vms = [LogViewModel(log) for log in logs]
	return render_template("admin_progress_logs.html", log_vms=log_vms)

@app.route("/admin/user_stats")
@login_required
def admin_user_stats():
	users = User.query.order_by(User.registered_on).all()
	user_vms = [UserViewModel(user) for user in users]

	return render_template("admin_user_stats.html", user_vms=user_vms)

@app.route("/admin/event_stats")
@login_required
def admin_event_stats():
	events = Event.query.all()
	event_vms = [EventLogViewModel(event) for event in events]

	return render_template("admin_event_stats.html", event_vms=event_vms)


@app.route("/admin/system_logs")
#@login_required
def admin_system_logs():
	syslogs = Error.query.all()
	return render_template("admin_system_logs.html", syslogs=syslogs)

# TODO: Put PowerToken setup instructions here (or just link to the document,
# which can be found in the GroupLens Google Drive under Meetings >
# ProDUCT Lab > Projects > PowerToken Wearables).
@app.route("/admin/instructions")
@login_required
def admin_instructions():
	return "Not implemented."

# TODO: Create some kind of help page, maybe with instructions on how to
# troubleshoot the PowerToken system. This should be more for study
# administrators than system administrators (i.e. more practical than
# technical).
@app.route("/admin/help")
@login_required
def admin_help():
	return "Not implemented."

@app.route("/admin/test")
def admin_test():
	users = User.query.order_by(User.registered_on).all()
	user_vms = [UserViewModel(user) for user in users]
	return render_template("admin_user_stats.html", user_vms=user_vms)
