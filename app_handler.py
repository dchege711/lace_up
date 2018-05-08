from flask import Flask, jsonify, make_response, request, render_template, send_file, url_for, redirect
from flask_cors import CORS
import os
from pprint import pprint

import sys
import os 

sys.path.insert(0, os.path.join(os.getcwd(), "back_end_scripts"))
 
import user_actions
import game_actions

app = Flask(__name__)

# Setting this to zero tells Flask to stop cacheing static assets
# like .js files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)   # Allow Cross-Origin-Resource-Sharing on all methods

# app_files = {
#     # "logo_cropped.png": send_file("./static/img/logo/logo_cropped.png", mimetype="image/png"),
#     "navigation.html": render_template("navigation.html")
# }

#_______________________________________________________________________________

# Global variables
current_user_account = None

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

@app.route('/footer.html')
def return_footer():
    """
    Returns the Page Footer. 
    
    """
    return render_template("footer.html")
    
@app.route('/register/', methods=["POST"])
def register_new_users():
    global current_user_account

    if request.method == "POST":
        """
        Process the information that was entered on the registration form.
        
        @returns (JSON): `success` will be True iff the registration was 
        successfully completed. 
        If `success` is `True`, `message` will have the following keys: 
        `user_id`, `first_name`, `games_joined`, `games_owned`, 
        `orphaned_games`, `session_token`.
        If `success` is `False`, `message` will contain a string explaining
        what went wrong.
        
        """
        payload = request.get_json()
        
        successfully_registered_user = user_actions.register_user(payload)["success"]
        if successfully_registered_user:
            current_user_account = user_actions.sport_together_user(
                {"email_address": payload["email_address"]}, 
                payload["password"]
            )

            return jsonify({
                "success": True,
                "message": current_user_account.return_user_info(
                    keys_to_use=[
                    "user_id", "first_name", "games_joined", "games_owned",
                    "orphaned_games", "session_token"
                ])
            })
        else:
            return jsonify({
                "success": False,
                "message": "Unsuccessful registration. Please try again after a few minutes."
            })
            
@app.route('/login/', methods=["POST"])
def handle_login():
    global current_user_account
    
    if request.method == "POST":
        """
        Process a login request.
         
        @returns (JSON): `success` will be True iff the registration was 
        successfully completed. 
        If `success` is `True`, `message` will have the following keys: 
        `user_id`, `first_name`, `games_joined`, `games_owned`, 
        `orphaned_games`, `session_token`.
        If `success` is `False`, `message` will contain a string explaining
        what went wrong.
        
        """
        
        payload = request.get_json()
        if payload is None:
            payload = request.form

        account_exists = user_actions.is_in_db({
            "email_address": payload["email_address"]
        })
        
        if not account_exists:
            print("Account doesn't exist.")
            return jsonify({
                "success": False,
                "message": "Incorrect email or password"
            })
            
        else:
            current_user_account = user_actions.sport_together_user(
                {
                    "email_address": payload["email_address"]
                }, payload["password"])

            if current_user_account.account is None:
                print("Wrong password submitted.")
                return jsonify({
                    "success": False,
                    "message": "Incorrect email or password"
                })
            
            else:
                return jsonify({
                    "success": True,
                    "message": current_user_account.return_user_info(
                        keys_to_use=[
                            "user_id", "first_name", "games_joined", "games_owned",
                            "orphaned_games", "session_token"
                        ])
                })
            
@app.route('/read_games/', methods=["POST"])
def read_trips():
    global current_user_account

    if request.method == "POST":
        try:
            payload = request.get_json()
            print("Payload:")
            print(payload)
            
            relevant_games = {}
            
            if "game_ids" in payload:
                relevant_games = game_actions.get_games(payload["game_ids"])
            
            elif "user_id" in payload:
                if current_user_account is not None and payload["user_id"] == current_user_account.account["user_id"]:
                    relevant_games = current_user_account.get_games()
            
            return jsonify(relevant_games)
             
        except KeyError as e:
            print("Error:")
            print(e.message)
            return {}
        
@app.route("/update_game/", methods=["POST"])
def update_trip():
    if request.method == "POST":
        payload = request.get_json()
        print("Payload:")
        pprint(payload)
        
        try:
            results = current_user_account.update_game(payload)

        except AttributeError:
            results = None
        
        print("Response:")
        pprint(results)
        return jsonify(results)

@app.route("/home/", methods=["GET", "POST"])
def serve_home_page():
    if request.method == "GET":
        """
        Display the home feed for the user.
        
        """
        return render_template("home.html")

#_______________________________________________________________________________

@app.route('/creategame/', methods=["GET","POST"])
def createGame():
    global current_user_account

    if request.method == "GET":
        """
        Show the page necessary for a user to create a game.

        """
        return render_template("create_event.html")

    elif request.method == "POST":
        """
        Process the information that was entered on the event form. 
        Return whether the event creation was successful or not.

        """

        payload = request.get_json()

        if current_user_account is not None and payload["user_id"] == current_user_account.account["user_id"]:
            new_game_id = current_user_account.add_game(payload)
        else:
            new_game_id = None
            return jsonify({
                "success": False,
                "messageGame": "Unsuccessful creation of game. Please try again after a few minutes."
            })
        
        if new_game_id is not None:
            return jsonify({
                "success": True,
                "messageGame": "Successful creation of game. We hope you have fun playing!"
            })


        
        if new_game_id is not None:
            return jsonify({
                "success": True,
                "messageGame": "Successful creation of game. We hope you have fun playing!"
            })

@app.errorhandler(404)
def notFoundError(error):
    return "Page Not Found", 404

#_______________________________________________________________________________

if __name__ == '__main__':
    app.run(debug=True)

#_______________________________________________________________________________

