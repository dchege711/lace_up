from flask import Flask, jsonify, make_response, request, render_template, send_file
from flask_cors import CORS
import os
from pprint import pprint

import filter_trips
from mongo_db_client import tiger_rides_db
import user_actions
import trip_actions

app = Flask(__name__)
CORS(app)   # Allow Cross-Origin-Resource-Sharing on all methods

# app_files = {
#     # "logo_cropped.png": send_file("./static/img/logo/logo_cropped.png", mimetype="image/png"),
#     "navigation.html": render_template("navigation.html")
# }

#_______________________________________________________________________________

@app.route('/')
def index():
    """
    This is our home page.
    
    """
    return render_template("index.html")

@app.route('/static/img/logo/logo_cropped.png', methods=["GET"])
def get_logo():
    """
    Returns the Tiger Rides logo. I'm planning on deprecating this and using the 
    app_files dictionary in an app.route() that catches all mismatches.
    
    """
    return send_file("./static/img/logo/logo_cropped.png", mimetype="image/png")

@app.route('/navigation.html')
def return_navbar():
    """
    Returns the Navigation Bar. I'm planning on deprecating this and using the 
    app_files dictionary in an app.route() that catches all mismatches.
    
    """
    return render_template("navigation.html")

@app.route('/search/', methods=['POST'])
def search_trips():
    """
    Searching for trips on the /search/ url returns all the trips being made.
    There's no need for password authentication for this (yet?)
    
    """
    if request.method == 'POST':
        state = request.get_json()["origin_state"]        
        list_of_attendees = filter_trips.get_travellers_from_state(state)
                
        results_in_html = """
        <div class='w3-responsive'><table class='w3-table-all'>
            <tr>
                <th>Name</th><th>Number of People Coming</th>
                <th>City</th><th>State</th>
            </tr>
        """
        for result in list_of_attendees:
            results_in_html = "".join([results_in_html, tiger_cards(result)])
            
        results_in_html = "".join([results_in_html, "</table></div>"])
        
        return jsonify(results_in_html)

def tiger_cards(attendee_details):
    """
    Create a pretty row for a html table that will contain the trips being made.
    
    """
    return ''.join([
        "<tr><td>", attendee_details["name"], "</td>",
        "<td>", attendee_details["size"], "</td>",
        "<td>", attendee_details["city"], "</td>",
        "<td>", attendee_details["state_abbr"], "</td>", "</tr>"
    ])
    
@app.route('/register/', methods=["POST", "GET"])
def register_new_users():
    if request.method == "GET":
        """
        Show the page necessary for a user to register for Tiger Rides.
        
        """
        return render_template("new_member_registration.html")
    
    
    elif request.method == "POST":
        """
        Process the information that was entered on the registration form.
        Return whether the reigstration was successful or not.
        
        """
        payload = request.get_json()
        
        found_duplicate = user_actions.is_in_db({"email_address": payload["email_address"]})
        if (found_duplicate):
            return jsonify({
                "registration_status": False,
                "registration_message": "That email address has already been taken."
            })
        
        successfully_registered_user = user_actions.register_user(payload)[0]
        if successfully_registered_user:
            return jsonify({
                "registration_status": True,
                "registration_message": "Successful registration. Now log in with your email address and password"
            })
        else:
            return jsonify({
                "registration_status": False,
                "registration_message": "Unsuccessful registration. Please try again after a few minutes."
            })
            
@app.route('/login/', methods=["GET", "POST"])
def handle_login():
    if request.method == "GET":
        """
        Display the login form for registered members.
        
        """
        return render_template("login.html")
    
    elif request.method == "POST":
        """
        Process a login request. 
        Deny authentication for users that submit wrong passwords.
        Otherwise, return the user's first name and their trips.
        
        """
        
        payload = request.get_json()
        account = user_actions.get_user({
            "email_address": payload["email_address"],
            "password": payload["password"]
        })
        
        if account is None:
            return jsonify({
                "login_successful": False,
                "login_payload": "Incorrect email or password"
            })
            
        else:
            return jsonify({
                "login_successful": True,
                "login_payload": {
                    "first_name": account["first_name"],
                    "trips_owned": account["trips_owned"],
                    "trips_joined": account["trips_owned"]
                }
            })
            
@app.route('/read_trips/', methods=["POST"])
def read_trips():
    if request.method == "POST":
        try:
            payload = request.get_json()
            print("Payload:")
            print(payload)
            
            trip_ids = []
            
            if "trip_ids" in payload:
                trip_ids = payload["trip_ids"]
            
            elif "user_id" in payload:
                user_trips = user_actions.get_trips(payload["user_id"])
                if payload["get_user_owned"]:
                    trip_ids = user_trips["trips_owned"]
                else:
                    trip_ids = user_trips["trips_joined"]
                    
            relevant_trips = trip_actions.get_trips(trip_ids)
            
            print("Response:")
            pprint(relevant_trips)
            return jsonify(relevant_trips)
             
        except KeyError as e:
            print("Error:")
            print(e.message)
            return {}
        
@app.route("/update_trip/", methods=["POST"])
def update_trip():
    if request.method == "POST":
        payload = request.get_json()
        print("Payload:")
        pprint(payload)
        
        results = trip_actions.update_trip(payload)
        
        print("Response:")
        pprint(results)
        return jsonify(results)

#_______________________________________________________________________________

@app.errorhandler(404)
def notFoundError(error):
    return "Page Not Found (︶︹︺)", 404

#_______________________________________________________________________________

if __name__ == '__main__':
    app.run()

#_______________________________________________________________________________
