#!/usr/bin/python3

# This Python script does the necessary WEconnect setup for the PowerToken
# project. It only needs to be run once.

import requests
import sys

# Makes sure the client has passed in the name of the script, the user's email,
# and the user's password.
if len(sys.argv) != 3:
    exit()

wcBaseUrl = "https://palalinq.herokuapp.com/api"
userEmail = sys.argv[1]
userPwd = sys.argv[2]
userId = ""
userToken = ""

# Logs user into WEconnect and produces an access token that will last 90 days.
result = requests.post(wcBaseUrl + "/People/login",
                       data={"email":userEmail, "password":userPwd})
if result.status_code != 200:
    print("Login error")
    exit()
jres = result.json()
userId = str(jres["accessToken"]["userId"])
userToken = str(jres["accessToken"]["id"])
print("Logged into WEconnect system.")

# Stores user's ID and access token in text file
with open("access.txt", "w+") as file:
    file.write(userId + "\n" + userToken)
