/*
 * Script that handles the Fitbit login process
 * Created by: Jasmine Jones
 * Last modified by: Abigail Franz on 1/19/2018
 */

var fbTok;

// If this boolean is set to false, the callback will just be localhost
var usingCsServer = true;
var isJasmine = false;

var clientID = '228N2H';
console.log('clientID = ' + clientID);

homeURL = '';
if (usingCsServer) {
	homeURL = 'https://powertoken.grouplens.org';
} else {
	homeURL = 'http://localhost:5000';
}
callback = homeURL + '/fb_login';
landingPage = homeURL + '/home';

var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';

// CHECK for returned code i.e. url#code, if no hash there, then redirect to auth site
if (!window.location.hash) {
	window.location.replace(authURI+'?response_type=token&client_id='+clientID+'&redirect_uri='+callback
		+'&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight');
} else {
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
		window.location.href = landingPage;
	}
}

// SEND token to server
if (fbTok) {
    console.log("redirecting back to app")
    fetch( homeURL+'/result', {
        method: 'POST', 
	   mode: 'no-cors',
	   body: JSON.stringify({tok: fbTok})
    })
    .then(processResponse)
}
