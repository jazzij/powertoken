"""
Handles routing and form processing for the PowerToken Flask app.\n
Created by Jasmine Jones\n
Last modified by Abigail Franz on 3/15/2018
"""

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import (
	current_user, login_user, logout_user, login_required
)
from werkzeug.urls import url_parse
from app import app, db, session
from app.forms import (
	AdminLoginForm, AdminRegistrationForm, UserLoginForm, UserWcLoginForm
)
from app.models import Admin, User, Log, Activity
from app.apis import login_to_wc, complete_fb_login

@app.route("/")
@app.route("/index")
@app.route("/home")
def user_home():
	if not "username" in session:
		return redirect(url_for("user_login"))
	else:
		return render_template("user_home.html", username=session["username"])

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
	form = UserLoginForm()

	# POST: processes the PowerToken login form
	if form.validate_on_submit():
		username = form.username.data
		print(username)
		session["username"] = username
		session.modified = True
		session.permanent = True
		user = User.query.filter_by(username=username).first()

		# If the user has not been added to the database, adds the user to the
		# database
		if user is None:
			user = User(username=username)
			db.session.add(user)
			db.session.commit()

			# Redirects to the WC login
			return redirect(url_for("user_wc_login"))
		
		# If the user exists in the database, and the WEconnect and Fitbit info
		# is already filled out, skips the login process.
		if (not user.wc_id is None) and (not user.wc_token is None) and \
			(not user.fb_token is None):
			return redirect(url_for("user_home"))

		# If the user exists in the database, but the WEconnect (or Fitbit)
		# info isn't filled out, redirects to WEconnect login.
		return redirect(url_for("user_wc_login"))

	# GET: renders the PowerToken login page
	return render_template("user_login.html", form=form)

@app.route("/user_wc_login", methods=["GET", "POST"])
def user_wc_login():
	form = UserWcLoginForm()

	# If submitting the form (POST)
	if form.validate_on_submit():
		user = User.query.filter_by(username=session["username"]).first()
		if user is None:
			return redirect(url_for("user_login"), errors=["Invalid user"])

		# Gets WEconnect info and adds it to the database
		email = form.email.data
		password = form.password.data
		result = login_to_wc(email, password)
		if not result:
			err = ["Incorrect email or password"]
			return render_template("user_wc_login.html", form=form, errors=err)
		user.wc_id = result[0]
		user.wc_token = result[1]
		db.session.commit()

		# Redirects to the Fitbit login
		return redirect(url_for("user_fb_login"))

	# If not submitting the form (GET)
	return render_template("user_wc_login.html", form=form)

@app.route("/user_fb_login", methods=["GET", "POST"])
def user_fb_login():
	# If submitting the external form (POST)
	if request.method == "POST":
		if not "username" in session:
			return redirect(url_for("user_login"))
		print("Inside user_fb_login(), session['username'] =  {}".format(session["username"]))
		user = User.query.filter_by(username=session["username"]).first()
		if user is None:
			return redirect(url_for("user_login"), errors=["Invalid user"])
		
		# Gets FB info and adds it to db
		fb_token = complete_fb_login(request.data)
		print(fb_token)
		user.fb_token = fb_token
		db.session.commit()

		# Redirects to welcome page when setup is finished
		print("Will be redirecting to homepage...")
		return

	# If requesting the redirect page (GET)
	elif request.method == "GET":
		return render_template("user_fb_login.html")

# Commenting out the login_required for ease of testing
@app.route("/admin")
@app.route("/admin/")
@app.route("/admin/index")
@app.route("/admin/home")
#@login_required
def admin_home():
	users = User.query.order_by(User.registered_on).all()
	pt_users = []
	for user in users:
		logs = user.logs.all()
		last_log = logs[-1] if len(logs) > 0 else \
			Log(daily_progress=0, weekly_progress=0, step_count=0, user=user)
		pt_users.append({
			"id": user.id,
			"username": user.username,
			"registered_on": user.registered_on.strftime("%Y-%m-%d %I:%M:%S %p"),
			"wc_status": "Current" if user.wc_id and user.wc_token else "Expired",
			"fb_status": "Current" if user.fb_token else "Expired",
			"daily_progress": last_log.daily_progress * 100,
			"weekly_progress": last_log.weekly_progress * 100
		})
	return render_template("admin_home.html", pt_users=pt_users)

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
#@login_required
def admin_progress_logs():
	logs = Log.query.order_by(Log.timestamp).all()
	return render_template("admin_progress_logs.html", logs=logs)

@app.route("/admin/user_stats")
#@login_required
def admin_user_stats():
	users = User.query.order_by(User.registered_on).all()
	return render_template("admin_user_stats.html", users=users)

@app.route("/admin/system_logs")
#@login_required
def admin_system_logs():
	return render_template("admin_system_logs.html")