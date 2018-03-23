/*
 * Script that handles the Fitbit login process
 * Created by: Jasmine Jones
 * Last modified by: Abigail Franz on 3/13/2018
 */

var fbTok;
var clientID = '228N2H';
var homeURL = 'https://powertoken.grouplens.org';
var callback = homeURL + '/user_fb_login';
var landingPage = homeURL + '/';
var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';

// CHECK for returned code i.e. url#code, if no hash there, then redirect to auth site
if (!window.location.hash) {
	console.log("Redirecting to Fitbit auth site")
	window.location.replace(authURI+'?response_type=token&client_id='+clientID+'&redirect_uri='+callback
		+'&scope=activity%20location%20profile%20settings');
} else {
	console.log("Getting access token from window.location.hash")
	var fragmentQueryParameters = {};
	window.location.hash.slice(1).replace(
		new RegExp("([^?=&]+)(=([^&]*))?", "g"),
		function($0, $1, $2, $3) { fragmentQueryParameters[$1] = $3; }
	);
	fbTok = fragmentQueryParameters.access_token;
}

var processResponse = function(response) {
	if (!response.ok) {
		console.log("response = " + response);
		throw new Error('Request failed' + response);
	} else {
		console.log("Switching to landing page from processResponse function");
		window.location.href = homeURL;
	}
}

// SEND token to server
if (fbTok) {
    console.log("fbTok = " + fbTok)
    fetch(callback, {
    	method: 'POST', 
		mode: 'no-cors',
		body: JSON.stringify({tok: fbTok})
    });
    //.then(processResponse)
}
