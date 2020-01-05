#Python WeConnect API call
import argparse, requests, sys, traceback, json
from datetime import datetime

wcBaseURL = "https://palalinq.herokuapp.com/api"
BASE_URL = "https://palalinq.herokuapp.com/api/people"

user = 'YOUR_USERNAME_HERE'
pw = 'YOUR_PASSWD_HERE'
token = None 

"""argument parsing for username and password"""
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--username", required=True, help="your WC username")
ap.add_argument("-p", "--password", required=True, help="your WC password")
args = vars(ap.parse_args())

 
#1a. login to get user data (POST).  I think all we need to save from the returned info is the token and the userID
def login( user, pw):
	req = requests.post(wcBaseURL+'/People/login', data={'email':user, 'password':pw})
	if req.status_code != 200:
		raise RuntimeError("Request could not be completed"+ req.status_code+req.text)
	else:
		print("Request success!")
	
	#convert to object
	jreq = req.json()
	userToken = jreq["accessToken"]["id"]
	userInfo = jreq["user"] #prob only useful data in this dict is [userId]
	
	return userToken, userInfo	

#1b. Retrieve user information if you already have the userID and accessToken (probably unnecessary)
def getPerson(userID, token):
	req = requests.get(wcBaseURL + '/People/'+id, params={'access_token':token})	
	if check(req):
		jreq = req.json()
		return jreq

#2. GET a list of all activities	
def getUserActivities(userID, token):
	print ("User info: {}, {}".format(userID, token))
	req = requests.get(wcBaseURL + '/People/'+userID+'/activities', params={'access_token':token})	
	if check(req):
		return req.json()

#3. GET a list of progress for all activities, date format 'YYYY-MM-DD'
def getUserActivitiesProgress(userID, token, fromDate, toDate):
	req = requests.get(wcBaseURL + '/People/'+userID+'/activities/progress', params={'access_token':token, 'from':fromDate, 'to':toDate})	
	if check(req):
		print('success')
		#return req.json()
	
	progress = req.json()
	#I think this is probs the key data want to use. 
	print("Total vs Completed Events in ", fromDate, "to ", toDate, ": ", progress["events"]["completed"],"/",  progress["events"]["total"])

	return progress	

def get_todays_events(userID, token):
	"""
	Get the activities-with-events that are happening today. Return an empty
	list if the request is unsuccessful.

	:param background.models.User user
	"""
	today = datetime.now()
	st = today.strftime("%Y-%m-%dT00:00:00")
	et = today.strftime("%Y-%m-%dT23:59:59")
	
	url = "{}/{}/activities-with-events?from={}&to={}&access_token={}".format(BASE_URL, userID, st, et, token)
	req = requests.get(url)
	if check(req):
		return req.json()
	else:
		return []
	
#helper code, just to make sure request was valid
def check(request):
	if request.status_code != 200:
		raise RuntimeError("Request could not be completed"+ req.status_code+req.text)
	else:
		print("Request success!")
		return True

''' RUN CODE '''
try:
	#your code here
	#example to get started: (uncomment below)
	user = args['username']
	pw = args['password']
	token, userInfo = login( user, pw)
	print( "Token: ", token)
	print( "User ID: ", userInfo["userId"])
	
	#print ( getUserActivities( str(userInfo["userId"]), str(token)))
	#print (getUserActivitiesProgress(str(userInfo["userId"]), str(token), ))
	print ( json.dumps( get_todays_events(str(userInfo["userId"]), str(token))))
	
except:
	#print('-'*60) 
	traceback.print_exc(file=sys.stderr)
	#print('-'*60)
