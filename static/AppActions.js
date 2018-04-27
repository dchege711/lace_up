function loadUserDetails(userDetails) {
    // Replace the navbar links with acknowledgement of the user loggin in
    document.getElementById("register_navbar_link").style.display = "none";
    document.getElementById("login_navbar_link").style.display = "none";
    document.getElementById("navbar_contents").insertAdjacentHTML(
        "beforeend",
        `<a href="/" class="w3-bar-item w3-button w3-padding-16 w3-hover-white w3-black w3-right">Log Out</a>
                    <span class='w3-bar-item w3-orange w3-right'><strong>Logged in as ` + userDetails.user_id + `</strong></span>`
    );

    var mainBody = document.getElementById("logged_in_contents");
    mainBody.innerHTML = `<p>These are your games</p>
                <div class='w3-responsive'> <table class='w3-table-all' id="user_owned_games"> <tr>
                <th>#</th><th>Type</th><th>Game ID</th><th>Location</th></th><th>Creator</th></th>
                <th>Also Attending</th><th>Edit</th></tr></table></div>
                <br><br>
                <p>You're also joining these games</p>
                <div class='w3-responsive'> <table class='w3-table-all' id="user_joined_games"> <tr>
                <th>#</th><th>Type</th><th>Game ID</th><th>Location</th></th><th>Creator</th></th>
                <th>Also Attending</th><th>Edit</th></tr></table></div>
                `;

    makeHttpRequest("POST", "/read_games/", { "user_id": userDetails.user_id }, function (results) {
        console.log("Loading user's games 123...");
        console.log(userDetails.games_owned)
        var tableElement = document.getElementById("user_owned_games");
        for (let i = 0; i < userDetails.games_owned.length; i++) {
            tableElement.insertAdjacentHTML(
                "beforeend", results.games_owned[i].html_version
            );
        }

        tableElement = document.getElementById("user_joined_games");
        for (let i = 0; i < userDetails.games_joined.length; i++) {
            tableElement.insertAdjacentHTML(
                "beforeend", results.games_joined[i].html_version
            );
        }
    });

    return false;
}

function makeHttpRequest(method, url, payload, callBack) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            callBack(JSON.parse(this.responseText));
        }
    }
    xhttp.open(method, url, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(payload));

    return false;
}

function logInMember() {

    var form = document.getElementById("login_form");
    if (form.reportValidity() === false) {
        alert("Please fill out the required fields");
        return;
    }

    var elements = form.elements;
    var payload = {};

    for (var i = 0; i < elements.length; i++) {
        payload[elements[i].name] = elements[i].value;
    }

    makeHttpRequest("POST", "/login/", payload, function(results) {
        console.log(results);
        if (results.success == true) {
            loadUserDetails(results.message);
        } else {
            alert(results.message);
        }
    });

    // We need to return false to prevent the page from 
    // reloading into a JSON object.
    return false;
}

function editGame(gameID) {
    var elementToBeModified = document.getElementById("logged_in_contents");
    elementToBeModified.insertAdjacentHTML("afterbegin", "<form id='game_to_be_changed'></form>");
    var formElement = document.getElementById("game_to_be_changed");
    formElement.innerHTML = `
        <p id="game_to_be_changed_id" style={"display":"none"}></p>
        <p id="game_to_be_changed_owner_id" style={"display": "none"}></p>
        
        <label for="origin">Time:</label>
        <input class="w3-input" type="text" name="origin" id="game_to_be_changed_origin" disabled/>
        <br />

        <label for="destination">Location:</label>
        <input class="w3-input" type="text" name="location" id="game_to_be_changed_location" disabled/>
        <br />
        
        <button class="w3-button w3-green" type="submit" onclick="return saveGame()">Save Changes</button>
    `
    makeHttpRequest("POST", "/read_games/", { "game_ids": [gameID] }, function (results) {
        var gameDetails = results[0];
        document.getElementById("game_to_be_changed_time").value = gameDetails.origin;
        document.getElementById("game_to_be_changed_location").value = gameDetails.destination;
        document.getElementById("game_to_be_changed_id").value = gameID;
        document.getElementById("game_to_be_changed_owner_id").value = parseInt(gameDetails.game_owner_id);
    });

    return false;
}

function saveGame() {
    var formElements = document.getElementById("game_to_be_changed").elements;
    var payload = {};
    for (var i = 0; i < formElements.length; i++) {
        payload[formElements[i].name] = formElements[i].value;
    }

    var userId = document.getElementById("game_to_be_changed_owner_id").value;
    payload.game_id = document.getElementById("game_to_be_changed_id").value;
    payload.game_owner_id = userId;
    delete payload[""];

    makeHttpRequest("POST", "/update_game/", payload, function (results) {
        document.getElementById("game_to_be_changed").style.display = "none";
        if (results.game_info !== false) {
            refreshGames(userId, true);
        }
    });

    return false;
}

function refreshGames(userId, get_user_owned) {
    var mainBody = document.getElementById("logged_in_contents");
    mainBody.innerHTML = `<p>These are your games</p>
                <div class='w3-responsive'> <table class='w3-table-all' id="user_owned_games"> <tr>
                <th>Game ID</th><th>Location</th><th>Time</th><th>Edit</th></tr></table></div>`;

    makeHttpRequest("POST", "/read_games/", { "user_id": userId }, function (results) {
        var tableElement = document.getElementById("user_owned_games");
        for (let i = 0; i < results.length; i++) {
            tableElement.insertAdjacentHTML("beforeend", results.games_owned[i].html_version);
        }
    });

    return false;
}