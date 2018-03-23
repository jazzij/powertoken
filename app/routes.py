"""
Handles routing and form processing for the PowerToken Flask app.\n
Created by Jasmine Jones\n
Last modified by Abigail Franz on 3/15/2018
"""

from datetime import datetime
from flask import (
	flash, redirect, render_template, request, session, url_for
)
from flask_login import (
	current_user, login_user, logout_user, login_required
)
from werkzeug.urls import url_parse
from app import app, db
from app.forms import (
	AdminLoginForm, AdminRegistrationForm, UserLoginForm, UserWcLoginForm
)
from app.models import Admin, User, Log, Activity
from app.apis import login_to_wc, complete_fb_login
from app.viewmodels import UserViewModel, LogViewModel

@app.route("/")
@app.route("/index")
@app.route("/home")
def user_home():
	# If the user is already logged in, display the homepage.
	if not "username" in session or not "authenticated" in session:
		print("'username' or 'authenticated' not in session, so redirecting to login.")
		return redirect(url_for("user_login"))

	# If the user isn't logged in, redirect to the PowerToken login.
	else:
		print("'username' and 'authenticated' in session, so showing the homepage,")
		return render_template("user_home.html", username=session.get("username"))

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
	form = UserLoginForm()

	# POST: processes the PowerToken login form
	if form.is_submitted():
		print("user_login form submitted.")
		if not form.validate():
			print("Form did not validate.")
		username = form.username.data
		session["username"] = username
		user = User.query.filter_by(username=username).first()

		# If the user has not been added to the database, add the user to the
		# database and redirect to the WEconnect login.
		if user is None:
			print("User {} isn't in the db yet. Adding to db".format(username))
			user = User(username=username)
			db.session.add(user)
			db.session.commit()
			print("Redirecting to WC login.")
			return redirect(url_for("user_wc_login"))
			
		# If the user exists in the database, but the WEconnect (or Fitbit)
		# info isn't filled out, redirect to the WEconnect login.
		if any([not user.wc_id, not user.wc_id, not user.fb_token]):# user.wc_id is None or user.wc_token is None or user.fb_token is None:
			print("Not all the info is filled out for {}. Redirecting to WC login.".format(user))
			return redirect(url_for("user_wc_login"))
			
		# If the user exists in the database, and the WEconnect and Fitbit info
		# is already filled out, bypass the login process.
		session["authenticated"] = True
		print("All info is filled out for {}. Redirecting to home.".format(user))
		return redirect(url_for("user_home"))

	# GET: Render the PowerToken login page.
	print("Received GET request for user_login page.")
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
		print("wc_login form submitted.")

		# If the username wasn't saved or the session expired, return to the
		# original PowerToken login page.
		if not "username" in session:
			print("'username' not in session.")
			return redirect(url_for("user_login", error="Invalid session"))

		# Get the user with that username from the database.
		user = User.query.filter_by(username=session.get("username")).first()

		# If the user with that username isn't in the database for whatever
		# reason, go back to the PowerToken login page.
		if user is None:
			print("User with username {} doesn't exist. Redirecting to user_login.".format(session.get("username")))
			return redirect(url_for("user_login", error="Invalid user"))

		# If everything is okay so far, get WEconnect info from the form and
		# login to external WEconnect server.
		email = form.email.data
		password = form.password.data
		successful_result = login_to_wc(email, password)

		# If the username or password is incorrect, prompt the user to re-enter
		# credentials.
		if not successful_result:
			print("Incorrect WC email or password. Reloading wc_login page.")
			errors = ["Incorrect email or password"]
			return render_template("user_wc_login.html", form=form, errors=errors)

		# If the login was successful, store the WEconnect ID and access token
		# in the database, and redirect to the Fitbit login.
		user.wc_id = successful_result[0]
		user.wc_token = successful_result[1]
		print("Updating {} with wc_id = {} and wc_token = {}".format(user, user.wc_id, user.wc_token))
		db.session.commit()
		print("Redirecting to fb_login.")
		return redirect(url_for("user_fb_login"))

	# GET: Render the WEconnect login page.
	print("Received GET request for wc_login page.")
	return render_template("user_wc_login.html", form=form)

@app.route("/user_fb_login", methods=["GET", "POST"])
def user_fb_login():
	# POST: Process response from external Fitbit server.
	if request.method == "POST":
		print("External fb_login POST data received.")

		# If the username wasn't saved or the session expired, return to the
		# original PowerToken login page.
		if not "username" in session:
			print("No field 'username' in session. Redirecting to user_login.")
			return redirect(url_for("user_login", error="Invalid session"))

		# Get the user with that username from the database.
		user = User.query.filter_by(username=session.get("username")).first()

		# If the user with that username isn't in the database for whatever
		# reason, go back to the PowerToken login page.
		if user is None:
			print("User with username {} doesn't exist. Redirecting to user_login.".format(session.get("username")))
			return redirect(url_for("user_login", error="Invalid user"))
		
		# If everything is okay so far, extract the Fitbit token from the
		# response data and add it to the database.
		fb_token = complete_fb_login(request.data)
		user.fb_token = fb_token
		print("Updating {} with fb_token = {}".format(user, user.fb_token))
		db.session.commit()

		# Redirect to welcome page when setup is finished
		session["authenticated"] = True
		print("Will be redirecting to homepage...")
		return redirect(url_for("user_home"))

	# If requesting the redirect page (GET)
	elif request.method == "GET":
		print("Received GET request for fb_login page.")
		return render_template("user_fb_login.html")

@app.route("/admin")
@app.route("/admin/")
@app.route("/admin/index")
@app.route("/admin/home")
@login_required
def admin_home():
	users = User.query.order_by(User.registered_on).all()
	user_vms = [UserViewModel(user) for user in users]
	return render_template("admin_home.html", user_vms=user_vms)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
	print("Called admin_login()")
	if current_user.is_authenticated:
		return redirect(url_for("admin_home"))
	form = AdminLoginForm()

	# POST: If a valid form was submitted
	if form.validate_on_submit():
		print("Submitted AdminLoginForm")
		admin = Admin.query.filter_by(username=form.username.data).first()
		if admin is None or not admin.check_password(form.password.data):
			flash("Invalid username or password")
			print("Invalid username or password")
			return redirect(url_for("admin_login"))
		login_user(admin, remember=form.remember_me.data)
		next_page = request.args.get("next")
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for("admin_home")
		print("next_page = {}".format(str(next_page)))
		return redirect(next_page)

	# GET: Renders the admin login template
	return render_template("admin_login.html", form=form)

@app.route("/admin/logout")
def admin_logout():
	logout_user()
	return redirect(url_for("admin_home"))

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
	if current_user.is_authenticated:
		return redirect(url_for("admin_home"))
	form = AdminRegistrationForm()
	if form.validate_on_submit():
		admin = Admin(username=form.username.data, email=form.email.data)
		admin.set_password(form.password.data)
		db.session.add(admin)
		db.session.commit()
		login_user(admin, remember=False)
		return redirect(url_for("admin_home"))
	return render_template("admin_register.html", form=form)

@app.route("/admin/progress_logs")
@login_required
def admin_progress_logs():
	logs = Log.query.all()
	log_vms = [LogViewModel(log) for log in logs]
	return render_template("admin_progress_logs.html", log_vms=log_vms)

@app.route("/admin/user_stats")
@login_required
def admin_user_stats():
	users = User.query.order_by(User.registered_on).all()
	user_vms = [UserViewModel(user) for user in users]
	return render_template("admin_user_stats.html", user_vms=user_vms)

@app.route("/admin/system_logs")
@login_required
def admin_system_logs():
	return render_template("admin_system_logs.html")