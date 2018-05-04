// Keep track of the different fields required for different forms
var requiredFields = {
    "registration_form": ["first_name", "last_name", "email_address", "password"],
    "login_form": ["email_address", "password"]
};

/**
 * @description Process the form and send the data to the appropriate url, then execute the callback.
 *
 * @param {string} formID The document id of the form element
 * @param {string} url The url to which the form data should be sent
 * @param {function} callBack The function to be called on success, takes the response as its parameter.
 */
function processFormAndPost(formID, url, callBack) {

    var form = document.getElementById(formID);
    var elements = form.elements;

    if (form.reportValidity() === false) {
        alert("Please fill out the required fields");
        return;
    }

    // Send the form to the server for further processing.
    var payload = {};
    for (var i = 0; i < elements.length; i++) {
        payload[elements[i].name] = elements[i].value;
    }
    delete payload[""];

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
    xhttp.onreadystatechange = function () {
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