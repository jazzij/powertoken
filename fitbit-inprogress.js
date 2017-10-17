var fbTok;

var clientID = '228N3P';
var callback = 'http://localhost/fitbit/fitbit.html';
var authURI = 'https://www.fitbit.com/oauth2/authorize';
var authTokenReq = 'https://api.fitbit.com/oauth2/token';
//'https://www.fitbit.com/oauth2/authorize?response_type=token&client_id=227H22&redirect_uri=https%3A%2F%2F15359f83.ngrok.io%2F&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight');
//"https://www.fitbit.com/oauth2/authorize&response_type=token&client_id=228N3P&redirect_uri=http://localhost/fitbit/fitbit.html&scope=activity"

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
	var header = document.querySelector('h1');

	best = JSON.stringify(activity["best"], null, 2);
	lifetime = JSON.stringify(activity["lifetime"], null, 2);
	tracker = JSON.stringify(activity["tracker"], null, 2);

	//prettyAct = JSON.stringify(activity, null, 2);
	//console.log(prettyAct)
	var display = document.getElementById('display');
//	var tempStr= "Data Retrieved:"+ "<br>";  
//				+ best + '<br />' 
//				+ lifetime +   
//				tracker;
//	console.log(tempStr);
	display.textContent = best;
	header.textContent = 'Fitbit - GET Activities';

	//playin around
	//convert to dic
//	var obj = JSON.parse(activity)
//	console.log(activity["best"]);
}

var processActivityWithDate = function(activity){
//	var disp=document.getElementById("display");
//	disp.innerHTML="hello<br/>hi";
	//GOALS (default 10K)
	var goalSteps = activity["goals"]["steps"];
	
	//STEPS BY ACTIVITY
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
	
	//SUMMARY STEPS TODAY
	var sumSteps = activity["summary"]["steps"];

	//print out the data
	var newpara = document.createElement("p");
        var dataStr = 'Goal Steps:' +goalSteps + '<br/>'
        	+ 'Steps by Activity: ' + activityStepsStr + '<br/>'        
        	+ 'Summary (total) Steps Today: '+ sumSteps;
	newpara.innerHTML = dataStr;
	
	var nextHeader = document.getElementById("otherHeader");
	document.body.insertBefore(newpara, nextHeader); 

//	console.log(JSON.stringify(activity, null, 2));
}


var activityUrl = 'https://api.fitbit.com/1/user/-/activities.json' // alternative ~/activities/date/[date].json
fetch( activityUrl, 
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


////////////////////
var goalPeriod = 'daily';
var goalPayload;// = JSON.parse('{"goals":{"activeMinutes":30,"caloriesOut":2297,"distance":8.05,"steps":10000}}');
var goalPostUrl = 'https://api.fitbit.com/1/user/-/activities/goals/'+goalPeriod+'.json';

var processGoal = function(goal){
	//goal = response.json();
	console.log( JSON.stringify(goal, null, 2));
	var goalPostPara = document.createElement("p");
	goalPostPara.innerHTML = 'New Goal Posted: '+ goal["goals"];
	document.body.insertBefore(goalPostPara, document.getElementById("otherHeader")); 
}

var alterGoal = function(goal){
	var goalStr = JSON.stringify(goal, null, 2);
	var goalObj = goal;//JSON.parse(goal);
	
	console.log(goalStr);
	console.log(goalObj["goals"]);
	console.log(goalObj["goals"]["steps"]);

	goal["goals"]["steps"] = 80;

	fetch( goalPostUrl,
        {
                headers: new Headers({
                        'Authorization': 'Bearer ' + fbTok
                }),
                mode: 'cors',
                method: 'POST',
                body: JSON.stringify(goal)
        }).then(processResponse).then(function(postResponse){ console.log('POST response: '+JSON.stringify(postResponse));})
        .catch(function(error){console.log(error);});

       //print out the data
//        var newpara = document.createElement("p");
//        var dataStr = 'Goal Steps:' +goalSteps + '<br/>';
//        newpara.innerHTML = dataStr;

//        var nextHeader = document.getElementById("otherHeader");
//        document.body.insertBefore(newpara, nextHeader);	
}


fetch( goalPostUrl,
        {
                headers: new Headers({
                        'Authorization': 'Bearer ' + fbTok
                }),
                mode: 'cors',
                method: 'GET'
        }
        ).then(processResponse)
	.then(alterGoal)
	.catch(function(error){console.log(error);});

console.log("end of script");
/*
fetch( goalPostUrl,
        {
                headers: new Headers({
                        'Authorization': 'Bearer ' + fbTok
               }),
                mode: 'cors',
                method: 'GET'
        }).then(processResponse)
	.then(processGoal)
        .catch(function(error){console.log(error);});

*/
