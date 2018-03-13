"""
Handles routing and form processing for the PowerToken Flask app.\n
Created by Jasmine Jones\n
Last modified by Abigail Franz on 3/13/2018
"""

from flask import flash, redirect, render_template, request, session, url_for
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
		user = User.query.filter_by(username=username).first()
		session["username"] = username
		session.modified = True

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
		if (not user.wc_id is None) and (not user.wc_token is None):
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
			flash("Invalid user")
			return redirect(url_for("user_login"))

		# Gets WEconnect info and adds it to the database
		email = form.email.data
		password = form.password.data
		print(email, password)
		wc_id, wc_token = login_to_wc(email, password)
		print(wc_id, wc_token)
		user.wc_id = wc_id
		user.wc_token = wc_token
		db.session.commit()

		# Redirects to the Fitbit login
		return redirect(url_for("user_fb_login"))

	# If not submitting the form (GET)
	return render_template("user_wc_login.html", form=form)

@app.route("/user_fb_login", methods=["GET", "POST"])
def user_fb_login():
	# If submitting the external form (POST)
	if request.method == "POST":
		user = User.query.filter_by(username=session["username"]).first()
		if user is None:
			flash("Invalid user")
			return redirect(url_for("user_login"))
		
		# Gets FB info and adds it to db
		fb_token = complete_fb_login(request.data)
		print(fb_token)
		user.fb_token = fb_token
		db.session.commit()

		# Redirects to welcome page when setup is finished
		return redirect(url_for("user_home"))

	# If requesting the redirect page (GET)
	elif request.method == "GET":
		return render_template("user_fb_login.html")

@app.route("/admin")
@app.route("/admin/")
@app.route("/admin/index")
@app.route("/admin/home")
@login_required
def admin_home():
	return render_template("admin_home.html")

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
	return render_template("admin_progress_logs.html")

@app.route("/admin/user_stats")
@login_required
def admin_user_stats():
	return render_template("admin_user_stats.html")

@app.route("/admin/system_logs")
@login_required
def admin_system_logs():
	return render_template("admin_system_logs.html")