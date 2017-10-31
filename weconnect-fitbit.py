# Pseudocode
# Poll progress at intervals, say of 1 hr
# If progress has changed since last poll, send updates to Fitbit
# See if we can listen for WEconnect updates
# See if we can do weekly (set week or 7 days from now?)
# Run from browser (CS server)
# Save token in text file (maybe encrypt?)

import datetime
import requests
import sys

wcBaseUrl = 'https://palalinq.herokuapp.com/api'
user = 'a2zfranz@gmail.com'
pw = 'daya2Beronad!'

class PowerToken:
    wcBaseUrl = "https://palalinq.herokuapp.com/api"
    _userEmail = ""
    _userPwd = ""
    _userId = ""
    _userToken = ""

    dailyStepGoal = 1000000
    
    def __init__(self, userEmail, userPwd):
        self._userEmail = userEmail
        self._userPwd = userPwd
        self.login()

    def login(self):
        result = requests.post(self.wcBaseUrl + "/People/login",
                            data={"email":self._userEmail,"password":self._userPwd})
        if self.isValid(result):
            jres = result.json()
            self._userId = str(jres["accessToken"]["userId"])
            self._userToken = str(jres["accessToken"]["id"])
            print("Logged in!")

    def poll(self):
        temp = datetime.datetime(1977, 1, 1)
        d = temp.today()
        currentDate = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
        currentTime = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        beginDate = currentDate + "T00:00:00"
        endDate = currentDate + "T" + currentTime
        percentProgress = self.getProgress(beginDate, endDate)
        print(percentProgress)
        stepsTaken = int(percentProgress * self.dailyStepGoal)
        # send stepsTaken to Fitbit in the form of a walking activity

    # GET a list of progress for all activities
    # Dates in format 'YYYY-MM-DD'
    def getProgress(self, fromDate, toDate):
        print("_userId:", self._userId)
        print("_userToken:", self._userToken)
        requestUrl = self.wcBaseUrl + "/People/" + self._userId + "/activities/progress?access_token=" + self._userToken + "&from=" + fromDate + "&to=" + toDate
        print(requestUrl)
        result = requests.get(requestUrl)	
        if self.isValid(result):
            progress = result.json()
            #I think this is probs the key data want to use. 
            print("Total vs Completed Events in ", fromDate, "to ", toDate, ": ",
                  progress["events"]["completed"],"/", progress["events"]["total"])
            percent = int(progress["events"]["completed"]) / int(progress["events"]["total"])
            return percent
        else:
            return -1

    def isValid(self, result):
        if result.status_code != 200:
            print("Request could not be completed:", str(result.status_code),
                  result.text)
            return False
        else:
            print("Request is valid!")
            return True

    
