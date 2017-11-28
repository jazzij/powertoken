var fbTok;

var clientID = '228N2H';
var callback = 'http://localhost:5000/fb_login'; //login.html'; //fitbit/fitbit.html';
var landingPage = 'http://localhost:5000/home';
var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';

// CHECK for returned code i.e. url#code, if no hash there, then redirect to auth site
if (!window.location.hash) {
	window.location.replace(authURI+'?response_type=token'+'&client_id='+clientID
													+'&redirect_uri='+callback+'&scope=activity%20weight');
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
		throw new Error('Request failed' + response);
	} else {
		window.location.href = landingPage;
	}
}

// SEND token to server
if (fbTok) {
	console.log("redirecting back to app")
	fetch('http://localhost:5000/result', {
		method: 'POST', 
		mode: 'no-cors',
		body: JSON.stringify({"tok": fbTok})
	})
	.then(processResponse)
	//.then( function(response){ if (response.ok) { return response.json()} })
	//.then(function(data){ window.location.replace('') })
}
