/*
 * This file defines some of the common functions used by fitbit_login.js and fitbit.js.
 */

var processResponse = function(response) {
    if (!response.ok) {
        throw new Error('Request failed: ' + response);
    } else {
		return response.json();
	}
}

var sendToFitbut = function(url, method, fbTok) {
    fetch(postUrl, {
        headers: new Headers({
            'Authorization': 'Bearer ' + fbTok
        }),
        mode: 'cors',
        method: method
    })
    .then(processResponse)
    .then(function(data) {
        console.log('The data I received from Fitbit: ' + JSON.stringify(data, null, 2));
    })
    .catch(function(error) {
        console.log('There was an error posting to the goal API: ' + error); 
    });
}