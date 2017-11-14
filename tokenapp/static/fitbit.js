/*
* This code is for the PowerTokens project. 
* OAuth2 flow adapted from sample code from JeremiahLee
* Uses Fetch & Fitbit Web API
*/

/*
 * Changes the user's step goal.
 */
var changeStepGoal = function(newStepGoal, fbTok) {
    var goalUrl = 'https://api.fitbit.com/1/user/-/activities/goals/daily.json';
    var postUrl = goalUrl + '?steps=' + newStepGoal;
    sendToFitbit(postUrl, 'POST', fbTok);
}

/* 
 * Increments the user's step count by creating a walking activity (activityId=17151)
 * with distance measured in steps.
 */
var updateStepCount = function(newStepCount, fbTok) {
    // Builds url that updated step count will be posted to
    var updateStepsUrl = 'https://api.fitbit.com/1/user/-/activities.json?activityId=17151';
    Date today = new Date();
    var startTime = today.getHours() + ':' + today.getMinutes() + ':' + today.getSeconds();
    var date = today.getYear() + '-' + today.getMonth() + '-' + today.getDay();
    var postUrl = updateStepsUrl + '&startTime=' + startTime + '&durationMillis=360000&date=' + date 
            + '&distance=' + newStepCount + '&distanceUnit=steps';

    // Actually updates the step count
    sendToFitbit(postUrl, 'POST', fbTok);
}

/*
 * Gets the user's current step goal.
 */
var getStepGoal = function(fbTok) {
    var activityGoalsUrl = 'https://api.fitbit.com/1/user/-/activities/goals/weekly.json';
    sendToFitbit(activityGoalsUrl, 'GET', fbTok);
}