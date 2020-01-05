from background.database import db_session, closeConnection
from data.models import User, Event, Activity

users = db_session.query(User).all()
events = db_session.query(Event).all()

for user in users:
	print("{} {} {}".format(user.username, user.wc_id, user.fb_token))

for user in users:
	user.wc_token = None
	user.fb_token = None
	user.fb_id = None
db_session.commit()

closeConnection()

