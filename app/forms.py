"""
Contains the form classes for the admin registration and login, the user login,
and the user WEconnect login.\n
Created by Abigail Franz on 3/12/2018\n
Last modified by Abigail Franz on 3/13/2018
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError
from app.models import Admin

class AdminLoginForm(FlaskForm):
	username = StringField("Username", validators=[InputRequired()])
	password = PasswordField("Password", validators=[InputRequired()])
	remember_me = BooleanField("Remember Me")
	submit = SubmitField("Sign In")

class AdminRegistrationForm(FlaskForm):
	username = StringField("Username", validators=[InputRequired()])
	email = StringField("Email", validators=[InputRequired(), Email()])
	password = PasswordField("Password", validators=[InputRequired()])
	password2 = PasswordField(
		"Repeat Password", validators=[InputRequired(), EqualTo("password")])
	submit = SubmitField("Register")

	def validate_username(self, username):
		admin = Admin.query.filter_by(username=username.data).first()
		if admin is not None:
			raise ValidationError("Please choose a different username.")

	def validate_email(self, email):
		admin = Admin.query.filter_by(email=email.data).first()
		if admin is not None:
			raise ValidationError("Please use a different email address.")

class UserLoginForm(FlaskForm):
	username = StringField("Username", validators=[InputRequired()])
	submit = SubmitField("Next")

class UserWcLoginForm(FlaskForm):
	email = StringField("Email", validators=[InputRequired(), Email()])
	password = PasswordField("Password", validators=[InputRequired()])
	#goal_period = RadioField("Goal Period", 
	#	choices=[("daily", "daily"), ("weekly", "weekly")])
	submit = SubmitField("Next")