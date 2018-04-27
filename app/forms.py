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
from app import db
from app.models import Admin, Activity

class AdminLoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
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

"""
class ActivityForm(FlaskForm):
	def __init__(self, activity):
		self.act_id = HiddenField(_prefix=activity.act_id)
		self.act_id.data = activity.act_id
		self.name = activity.name
		choices = [('1', '1'), ('2, 2'), ('3', '3'), ('4', '4'), ('5', '5')]
		self.weight = SelectField(choices=choices, _prefix=activity.act_id)
"""

class ModelFieldList(FieldList):
	def __init__(self, *args, **kwargs):         
		self.model = kwargs.pop("model", None)
		super(ModelFieldList, self).__init__(*args, **kwargs)
		if not self.model:
			raise ValueError("ModelFieldList requires model to be set")

	def populate_obj(self, obj, name):
		while len(getattr(obj, name)) < len(self.entries):
			newModel = self.model()
			db.session.add(newModel)
			getattr(obj, name).append(newModel)
		while len(getattr(obj, name)) > len(self.entries):
			db.session.delete(getattr(obj, name).pop())
		super(ModelFieldList, self).populate_obj(obj, name)

class ActivityForm(Form):
	activity_id = HiddenField("Activity ID")
	name = StringField("Name")
	weight = SelectField("Weight", choices=[(c, c) for c in [1', '2', '3', '4', '5']])
	def __init__(self, csrf_enabled=False, *args, **kwargs):
		super(ActivityForm, self).__init__(csrf_enabled=False, *args, **kwargs)

class UserActivityForm(FlaskForm):
	#activities = []
	submit = SubmitField("Next")
	activities = ModelFieldList(FormField(ActivityForm), model=Activity)

	"""
	def __init__(self, activities=[]):
		super(UserActivityForm, self).__init__()
		_choices = [('1', '1'), ('2, 2'), ('3', '3'), ('4', '4'), ('5', '5')]
		for act in activities:
			act_field = SelectField(label=act.name, choices=_choices, 
					_prefix=act.activity_id)
			self.activities.append(act_field)
	"""