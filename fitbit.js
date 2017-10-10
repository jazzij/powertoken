/*
* This code is for the PowerTokens project. 
* OAuth2 flow adapted from sample code from JeremiahLee
* Uses Fetch & Fitbit Web API
*/
var fbTok;

var clientID = 'YOUR_ID_HERE';
var callback = 'YOUR_WEBSITE_HERE'; 
var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';

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

var processActivity = function(activity){
	prettyAct = JSON.stringify(activity, null, 2);
	console.log(prettyAct)
//	var display = document.getElementById('display');
	var desplay = document.querySelector('p');
//	display.textContent = prettyAct;
	desplay.textContent = 'New stuff: ' + prettyAct;
}

fetch( 'https://api.fitbit.com/1/user/-/activities.json', 
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
