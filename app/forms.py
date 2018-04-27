"""
Contains the form classes for the admin registration and login, the user login,
and the user WEconnect login.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 3/13/2018.
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, 
	RadioField, HiddenField, FieldList, FormField, IntegerField, SelectField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import Admin

class AdminLoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField("Remember Me")
	submit = SubmitField("Sign In")

class AdminRegistrationForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	password2 = PasswordField(
		"Repeat Password", validators=[DataRequired(), EqualTo("password")])
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
	username = StringField("Username", validators=[DataRequired()])
	submit = SubmitField("Next")

class UserWcLoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Next")

class ActivityForm(FlaskForm):
	def __init__(self, activity):
		self.act_id = HiddenField(_prefix=activity.act_id)
		self.act_id.data = activity.act_id
		self.name = activity.name
		choices = [('1', '1'), ('2, 2'), ('3', '3'), ('4', '4'), ('5', '5')]
		self.weight = SelectField(choices=choices, _prefix=activity.act_id)

class UserActivityForm(FlaskForm):
	username = HiddenField("Username")
	submit = SubmitField("Next")
	activities = []
	_choices = [('1', '1'), ('2, 2'), ('3', '3'), ('4', '4'), ('5', '5')]

	def __init__(self, activities=[], username=None):
		self.username.data = username
		for act in activities:
			act_field = SelectField(label=act.name, choices=_choices, 
					_prefix=act.activity_id)
			self.activities.append(act_field)