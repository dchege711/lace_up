var requiredFields = {
        "event_form": ["type", "location", "date", "time", "numPlayers"]
    }
    /**
     * @description Process the form and send the data to the appropriate url, then execute the callback.
     *
     * @param {string} formID The document id of the form element
     * @param {string} url The url to which the form data should be sent
     * @param {function} callBack The function to be called on success, takes the response as its parameter.
     */

function eventFormAndPost(formID, url, callBack) {

    var form = document.getElementById(formID);
    var elements = form.elements;

    if (form.reportValidity() === false) {
        alert("Please fill out the required fields.");
        return;
    }

    // Send the form to the server for further processing.
    var payload = {};
    for (var i = 0; i < elements.length; i++) {
        payload[elements[i].name] = elements[i].value;
    }
    delete payload[""];
    payload.user_id = localStorage.getItem("user_id")

    console.log("Payload: ")
    console.log(payload)

    sendHTTPRequest("POST", url, payload, callBack);
}

/**
 *
 * @param {string} method The method to be used, e.g. "POST"
 * @param {string} url The url to which the payload will be sent
 * @param {JSON} payload The payload that will be sent.
 * @param {function} callBack The callback function once the request is successful
 */
function sendHTTPRequest(method, url, payload, callBack) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callBack(JSON.parse(this.responseText));
        }
    }
    xhttp.open(method, url, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(payload));

}

/**
 * Some divs need to be the same height. This function takes care of that.
 * It's been duplicated in AppActions.js too
 */
function resizeElements() {
    var height = $("#navigation-snippet").height();
    $("#dummy_padded_div").height(height);
}


//var debug = true;

/**
 * @description Process the form and send the data to the appropriate url, then execute the callback.
 *
 * @param {string} formID The document id of the form element
 * @param {string} url The url to which the form data should be sent
 * @param {function} callBack The function to be called on success, takes the response as its parameter.
 */
/** 
function eventForm(formID, url, callBack) {
    var elements = document.getElementById(formID).elements;
    var missingElements = checkRequired(elements, formID);

    if (debug) console.log("Called the correct event form");

    if (missingElements.size >= 1) {
        if (debug) console.log("Missing elements in create game form");
        missingElements.forEach(function(elementName) {
            // document.getElementById(elementName).style.border = "thin solid red";
        });

        callBack({
            "success": false,
            "message": "Please fill in the required fields."
        })
        return false;
    } else {
        // Send the form to the server for further processing.
        var payload = {};
        for (var i = 0; i < elements.length; i++) {
            payload[elements[i].name] = elements[i].value;
        }
        delete payload[""];
        payload["user_id"] = localStorage.getItem("user_id")
        console.log("Payload being sent...")
        console.log(payload)
        sendHTTPRequest("POST", url, payload, callBack);

    }
}
*/
/**
 * @returns {boolean} true if the element's value is blank, false otherwise.
 * @param {string} elementValue The element to be checked
 */
/**
function isBlank(elementValue) {
    return elementValue.trim() === "";
}
*/
/**
 * @description Check whether all required fields have been completed.
 *
 * @param {HTMLFormElement} elements The contents of the form element
 * @param {string} formID The document ID of the form
 */
/** 
function checkRequired(elements, formID) {
    var requiredElements = requiredFields[formID];
    var missingElements = new Set();
    requiredElements.forEach(function(name) {
        console.log("Name: " + name);
        console.log(elements[name].value)
        if (isBlank(elements[name].value)) {
            missingElements.add(name);
        }
    });
    return missingElements;
}
*/
/**
 *
 * @param {string} method The method to be used, e.g. "POST"
 * @param {string} url The url to which the payload will be sent
 * @param {JSON} payload The payload that will be sent.
 * @param {function} callBack The callback function once the request is successful
 */
/** 
function sendHTTPRequest(method, url, payload, callBack) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callBack(JSON.parse(this.responseText));
        }
    }
    xhttp.open(method, url, true);
    console.log("This is the payload being sent...")
    console.log(payload);

    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(payload));
}
*/