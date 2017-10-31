# This Python script does the necessary WEconnect setup for the PowerToken
# project. It only needs to be run once.

import requests

wcBaseUrl = "https://palalinq.herokuapp.com/api"
userEmail = "a2zfranz@gmail.com"
userPwd = "daya2Beronad!"
userId = ""
userToken = ""

# Logs user into WEconnect and produces an access token that will last 90 days
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
