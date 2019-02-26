"""
DB UTIL
Verify if user is present
Put user info into database

"""
from powertoken.models import User, Activity, Event
from powertoken import db
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def close_session():
	db.session.remove()

def pt_userExists(username):
	''' RETURNS TRUE | FALSE '''
	user= User.query.filter_by(username=username).first()
	if user is None:
		return False
	else:
		return True

def pt_userProfileComplete(username):
	''' RETURNS TRUE | FALSE '''
	if pt_userExists(username):
		user= User.query.filter_by(username=username).first()
		if any ([not user.wc_id, not user.wc_token, not user.fb_token]):
			return False
		else:
			return True	
	else:
		return False

def pt_addUser(username):
	''' RETURNS TRUE | FALSE '''
	user= User(username=username)
	db.session.add(user)
	errorMsg = None
	
	db.session.commit()
	#TODO: try-except error when same name is added
	'''except OperationError:
		#undo staged changes and report error
		db.session.rollback()
		errorMsg = "User with username {} already exists".format(username)
		logging.debug(errorMsg)
		return errorMsg
	finally:
		#db.session.close()
		logging.info("User {} added".format(username))	
		return errorMsg'''
	
def wc_addInfo(username, wc_id, wc_token, activities):
		
	user = db.session.query(User).filter_by(username=username).first()
	user.wc_id = wc_id
	user.wc_token = wc_token
	
	for act in activities:
		db.session.add( Activity(wc_act_id=act["id"], name=act["name"], expiration=act["expiration"], user=user))
	
	db.session.commit()
	
	errorMsg = None
	return errorMsg
	'''
	try:
		db.session.commit()
	except:
		db.session.rollback()
		errorMsg = "User with same WC credentials already exists"
	finally:
		return errorMsg
	'''
	
def fb_addInfo(username):
	user= User.query.filter_by(username=username).first()
	user.fb_token = fb_token
	
	errorMsg = None
	try:
		db.session.commmit()
	except:
		db.rollback()
		errorMsg = "User with username already exists"

	return errorMsg
