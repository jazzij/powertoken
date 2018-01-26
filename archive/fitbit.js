/*
* This code is for the PowerTokens project. 
* OAuth2 flow adapted from sample code from JeremiahLee
* Uses Fetch & Fitbit Web API
*
* This work is shared under the MIT License, 2017 (jazzij). Please feel free to use & share, but attribute appropriately. 
*/

//VARIOUS KEYS and AUTH IDS needed
var fbTok;
var clientID = 'YOUR_ID_HERE';
var callback = 'YOUR_WEBSITE_HERE'; 
var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';

// Implementing 'Implicit Auth in OATH2.0'
if (!window.location.hash){
	window.location.replace( authURI+'?response_type=token'+'&client_id='+clientID
		+'&redirect_uri='+callback+'&scope=activity');
} else{
    var fragmentQueryParameters = {};
    window.location.hash.slice(1).replace(
        new RegExp("([^?=&]+)(=([^&]*))?", "g"),
        function($0, $1, $2, $3) { fragmentQueryParameters[$1] = $3; }
    );
    
    fbTok = fragmentQueryParameters.access_token;
}

// HANDLE the response from FITBIT API (expect JSON)
var processResponse = function(response){
	if (!response.ok){
		throw new Error('Fitbit API request failed' + response);
	}
	var contentType = response.headers.get('content-type')
	if(contentType && contentType.indexOf("application/json") !== -1){
		document.querySelector('h2').textContent = 'JSON recieved!';
		return response.json();
	}else{		
		throw new Error('JSON expected but received'+contentType);
	}
}

/**************** GET DATA *****************/
// HANDLE the data from an /ACTIVITY api endpoint - summary data
var processActivity = function(activity){
	document.getElementById('activityHeader').textContent = 'Fitbit - GET Activity';
	prettyAct = JSON.stringify(activity, null, 2);
	console.log(prettyAct)
	
	//these are the three "elements" of data returned in the activity summary
	best = JSON.stringify(activity["best"], null, 2);
	lifetime = JSON.stringify(activity["best"], null, 2);
	tracker = JSON.stringify(activity["tracker"], null, 2);
	
	var display = document.getElementById('display');
	display.textContent = best;
}

//HANDLE data from /Activity/Date api endpoint - get actual step count data
var processActivityWithDate = function(activity){
        //get GOALS (default 10K)
        var goalSteps = activity["goals"]["steps"];

        //get STEPS BY ACTIVITY
        var activitySteps = {};
        var actArray = activity["activities"];
        var len = actArray.length;
        for ( var i = 0; i < len; i++){
                var id = actArray[i]["logId"];
                var steps = actArray[i]["steps"];
                console.log(id+ ': '+steps);
                activitySteps[id] = steps;
        }
        var activityStepsStr = JSON.stringify(activitySteps, null, 2);

        //get SUMMARY STEPS TODAY
        var sumSteps = activity["summary"]["steps"];

        //print out the data (buggy, need to figure out how to print new lines in javascript!)
        var newpara = document.createElement("p");
        var dataStr = 'Goal Steps:' +goalSteps + '<br/>'
        	+ 'Steps by Activity: ' + activityStepsStr + '<br/>'        
        	+ 'Summary (total) Steps Today: '+ sumSteps + '<br/>';
	newpara.innerHTML = dataStr;
	
        var nextHeader = document.getElementById("otherHeader");
        document.body.insertBefore(newpara, nextHeader);
//      console.log(JSON.stringify(activity, null, 2));
}

// Now, actually go forth and FETCH Activity Summary data
var activityURL = 'https://api.fitbit.com/1/user/-/activities.json';
fetch( activityURL, 
	{
		headers: new Headers({
			'Authorization': 'Bearer ' + fbTok
		}),
		mode: 'cors',
		method: 'GET'
	}
	).then(processResponse)
	.then(processActivity)
	.catch(function(error){ console.log(error);});

//go forth and fetch Daily Activity Data (much more detail)
var date = '2017-10-10';
var activityWithDateUrl = 'https://api.fitbit.com/1/user/-/activities/date/'+date+'.json';
fetch( activityWithDateUrl,
        {
                headers: new Headers({
                        'Authorization': 'Bearer ' + fbTok
                }),
                mode: 'cors',
                method: 'GET'
        }
        ).then(processResponse)
        .then(processActivityWithDate)
        .catch(function(error){ console.log(error);});

/***************** POST Data *************************/
//note: you can use these same URL's for GETting data, just change the the request type
var baseURL = 'https://api.fitbit.com/1/user/-/';
var dailyGoalURL = 'activities/goals/daily.json';
var logWeightURL = 'body/log/weight/goal.json';


//UPDATE DAILY STEP COUNT GOAL
//SAMPLE OUTPUT: {"goals":{"activeMinutes":45,"caloriesOut":2297,"distance":8.05,"steps":25000}} 
fetch( baseURL+dailyGoalURL+'?steps=25000',
        {
                method: 'POST',
                headers: new Headers({
                        'Authorization': 'Bearer ' + fbTok,
                }),
                mode: 'cors',
        }
        ).then(processResponse)
        .then(function(data){ console.log('Request succeeded with response', data);})
        .catch(function(error){ console.log(error.message);});

//ADD A BODY WEIGHT GOAL
//SAMPLE OUTPUT: {goalType: "LOSE", startDate: "2017-10-18", startWeight: 65.7, weight: 63, weightThreshold: 0.05}
fetch( baseURL+testURL+"?startDate=2017-10-18&startWeight=65.7&weight=63",
        {
                method: 'POST',
                headers: new Headers({
                        'Authorization': 'Bearer ' + fbTok,
                }),
                mode: 'cors',
        }
        ).then(processResponse)
        .then(function(data){ console.log('Request succeeded with response', data);})
        .catch(function(error){ console.log(error.message);});
