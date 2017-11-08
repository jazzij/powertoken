var fbTok;

var clientID = '228N3P';
var callback = 'http://localhost/fitbit/fitbit.html';
var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';

if (!window.location.hash){
	window.location.replace( authURI+'?response_type=token'+'&client_id='+clientID
		+'&redirect_uri='+callback+'&scope=activity%20weight');
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
		console.log( 'JSON recieved!');
		return response.json();
	}else{		
		throw new Error('JSON expected but received'+contentType);
	}
}

var baseURL = 'https://api.fitbit.com/1/user/-/';
var testURL = 'body/log/weight/goal.json'; 
var testURL2 = 'activities/goals/daily.json';
var testURL3 = 'body/log/fat/goal.json';
var actTestURL = "activities/goals/daily.json";

var urlStr = baseURL+ testURL3;

var processTestUrl = function(newData){
	console.log( newData);
	var display = document.getElementById("display1");
	display.innerHTML= JSON.stringify(newData);
}

var postWeight = function (){
	//var weight = {};
	var param = "fat=22.50";
}
/*
fetch( (urlStr), 
	{
		headers: new Headers({
			'Authorization': 'Bearer ' + fbTok
		}),
		mode: 'cors',
		method: 'GET'
	}
	).then(processResponse)
	.then(processTestUrl)
	.catch(function(error){ console.log(error);});
*/

fetch( 'https://api.fitbit.com/1/user/-/activities/goals/daily.json?steps=25000',
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






var bodyParam = "fat=22.50";
var actParam = "period=daily&type=steps&value=20000";
//THIS has error : {errorType: "validation", fieldName: "fat", message: "fat field is required."}
fetch( urlStr+"?"+bodyParam,
        {
		method: 'POST',
                headers: new Headers({
			'Authorization': 'Bearer ' + fbTok,
			
		}),
		mode: 'cors',
		body: JSON.stringify({"goal":{"fat":25.50}}) 
	}
        ).then(processResponse)
        .then(function(data){ console.log('Request succeeded with response', data);})
        .catch(function(error){ console.log(error.message);});


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

