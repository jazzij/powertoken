#Python WeConnect API call
import requests, sys

wcBaseURL = 'https://palalinq.herokuapp.com/api'
user = 'YOUR_USERNAME_HERE'
pw = 'YOUR_PASSWD_HERE'
token = None 
 
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
	req = requests.get(wcBaseURL + '/People/'+id+'/activities', params={'access_token':token})	
	if check(req):
		return req.json()

#3. GET a list of progress for all activities, date format 'YYYY-MM-DD'
def getUserActivitiesProgress(userID, token, fromDate, toDate):
	
	req = requests.get(wcBaseURL + '/People/'+id+'/activities/progress', params={'access_token':token, 'from':fromDate, 'to':toDate})})	
	if check(req):
		print('success')
		#return req.json()
	
	progress = req.json()
	#I think this is probs the key data want to use. 
	print("Total vs Completed Events in ", fromDate, "to ", toDate, ": ", progress["events"]["completed"],"/",  progress["events"]["total"])

	return progress	
		
#helper code, just to make sure request was valid
def check(request):
	if req.status_code != 200:
		raise RuntimeError("Request could not be completed"+ req.status_code+req.text)
	else:
		print("Request success!")
		return True


try:
	#your code here
	#example to get started: (uncomment below)
	token, userInfo = login( user, pw)
	print( "Token: ", token)
	print( "User ID: ", userInfo["userId"])
	
	print ( getUserActivities( userInfo["userId"], token))
	print (getUserActivitiesProgress(userInfo["userId"], token))
	
except Exception as ex: 
	print("Exception found: ", ex, file=sys.stderr)
