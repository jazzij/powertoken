/*
* This code is for the PowerTokens project. 
* OAuth2 flow adapted from sample code from JeremiahLee
* Uses Fetch & Fitbit Web API
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

// HANDLE the data from an /ACTIVITY api endpoint
var processActivity = function(activity){
	document.getElementById('activityHeader').textContent = 'Fitbit - GET Activity';
	prettyAct = JSON.stringify(activity, null, 2);
	console.log(prettyAct)
	var display = document.getElementById('display');
	display.textContent = prettyAct;
	
}

// Now, actually go forth and FETCH
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
