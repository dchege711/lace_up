from flask import Flask, jsonify, make_response, request, render_template, send_file
from flask_cors import CORS
import os
from pprint import pprint

import sys
import os 

sys.path.insert(0, os.path.join(os.getcwd(), "back_end_scripts"))
 
import user_actions
import game_actions

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
    Returns the Sport Together logo. I'm planning on deprecating this and using the 
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
        
        successfully_registered_user = user_actions.register_user(payload)["success"]
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
        account_exists = user_actions.is_in_db({
            "email_address": payload["email_address"]
        })
        
        if not account_exists:
            return jsonify({
                "success": False,
                "message": "Incorrect email or password"
            })
            
        else:
            fetch_account = user_actions.sport_together_user(
                {
                    "email_address": payload["email_address"]
                }, payload["password"])

            if fetch_account.account is None:
                return jsonify({
                    "success": False,
                    "message": "Incorrect email or password"
                })
            
            else:
                return jsonify({
                    "success": True,
                    "message": fetch_account.return_user_info()
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
    return "Page Not Found", 404

#_______________________________________________________________________________

if __name__ == '__main__':
    app.run()

#_______________________________________________________________________________
