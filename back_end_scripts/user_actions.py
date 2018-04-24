import secrets
import string
from random import choice
import bcrypt
from datetime import datetime

from mongo_db_client import sport_together_db
import game_actions

"""
Why the division between `users_db` and `login_db`?

The separation is only artificial. They both exist on the same
database. I wanted to simulate a situation where the credentials
are stored separate from the account information.

"""
users_db = sport_together_db("sport_together_user_account_info")
login_db = sport_together_db("sport_together_user_logins")

def is_in_db(key_val_pair, collection_to_use="login_db"):
    """
    @param `key_val_pair` (JSON): A key-value pair that might be
    associated with an account in the database.

    @return `True` if the key-value pair exists in the database.
    """
    if collection_to_use == "login_db":
        if login_db.read(key_val_pair) is not None:
            return True 
        else:
            return False
    else:
        if users_db.read(key_val_pair) is not None:
            return True
        else:
            return False

def get_user(key_val_pairs):
    """
    Fetch the account information for the user associated with
    the `key_val_pairs`.

    @param `key_val_pair` (JSON): A key-value pair that might be
    associated with an account in the database.

    @return (JSON): The user's account information
    """
    user_info = users_db.read(key_val_pairs)
    user_info.pop("_id", None)
    return user_info

def get_games(user_id):
    """
    Fetch all the games that the user has created or joined.

    @param `user_id` (String): The ID of the user.

    @returns: (JSON): Contains the keys `games_owned` and
    `games_joined`.

    """
    user_profile = users_db.read({"user_id": user_id})
    
    if user_profile is None:
        return {
            "games_owned": None, "games_joined": None
        }
    
    games = {}
    games["games_owned"] = user_profile["games_owned"]
    games["games_joined"] = user_profile["games_joined"]
    
    return games

def update_user_append(new_user_info):
    """
    Append new information to existing information on the user's
    profile.

    @param `new_user_info` (JSON): A JSON object with the info to
    be appended. `user_id` must be one of the keys in the JSON

    @return (JSON): Contains the key `user_info` that is `None`
    only if the update wasn't successful.

    """
    assert "user_id" in new_user_info, "`user_id` should have been specified"

    user_to_modify = users_db.read(
        {
            "user_id": new_user_info.pop("user_id", None)
        }
    )
    
    for key in new_user_info:
        # This is an inplace function!
        try:
            user_to_modify[key].append(new_user_info[key])
        except KeyError:
            user_to_modify[key] = [new_user_info[key]]

    return update_user(user_to_modify)

def update_user(new_user_info):
    """
    Overwrite the information in the user account.

    @param `new_user_info` (JSON): A JSON object with the info to
    be appended. `user_id` must be one of the keys in the JSON

    @return (JSON): Contains the key `user_info` that is `None`
    only if the update wasn't successful.

    @warning: This method overwrites existing fields. Use 
    `user_actions.update_user_append(new_user_info)` if you wish
    to append.

    """
    assert "user_id" in new_user_info, "`user_id` should have been specified"

    update_results = {}
    result = users_db.update(
        {
            "user_id": new_user_info["user_id"]
        }, new_user_info
    )
    if result.modified_count == 1:
        update_results["user_info"] = new_user_info
    else:
        update_results["user_info"] = None
            
    return update_results    

def delete_user(user_id):
    """
    Delete the user's account from Sport Together.

    @param `key_val_pair` (JSON): A key-value pair that might be
    associated with an account in the database.

    """
    login_db.delete({"user_id": user_id})
    user_account_info = users_db.delete({"user_id": user_id})

    if user_account_info is None:
        return None

    for game_id in user_account_info["games_joined"]:
        game_actions.remove_user_from_game(game_id, user_id)

    for game_id in user_account_info["games_owned"]:
        game_actions.remove_user_from_game(game_id, user_id)

    return True

def check_mandatory_fields(user_info):
    """
    @raises `KeyError` exception if `user_info` doesn't have
    enough information to create a new user account.

    """
    for expected_key in ("email_address", "password"):
        if expected_key not in user_info.keys():
            raise KeyError(
                "Did not find `", expected_key, "` as a key in `game_info`"
            )

def register_user(new_user_info):
    """
    Register a new user. 

    @param `new_user_info` (JSON): The registration details of the
    new user. Expected keys: `email_address`, `password`.

    @returns (JSON): Expected keys: `success`, `message`.

    """
    check_mandatory_fields(new_user_info)

    # We won't allow accounts that have more than one email address
    if is_in_db({"email_address": new_user_info["email_address"]}):
        return {
            "success": False,
            "message": "This email is already taken"
        }

    # Get a unique ID for each user. This ID should be different from database ID
    alphabet = string.digits
    while True:
        new_user_id = "".join(choice(alphabet) for i in range(10))
        if users_db.read({"user_id": new_user_id}) is None:
            break

    if "username" in new_user_info:
        username = new_user_info["username"]
    else:
        username = None

    salt = bcrypt.gensalt(rounds=12)
    hashed_pw = bcrypt.kdf(
        password=new_user_info["password"].encode(),
        salt=salt, desired_key_bytes=32, rounds=100
    )
    validation_url = secrets.token_urlsafe(32)

    insert_results_login = login_db.create({
        "email_address": new_user_info["email_address"],
        "username": username, "salt": salt, "hash": hashed_pw,
        "validation_url": validation_url, "already_validated": False,
        "signup_time": datetime.today().timestamp() 
    })

    assert insert_results_login.inserted_id is not None, "Failed to insert login details into the database"

    insert_results = users_db.create({
        "user_id": new_user_id, "games_joined": [],
        "games_owned": [], "orphaned_games": []
    })
    
    if insert_results.inserted_id is not None:
        return {
            "success": True, "message": new_user_id
        }
    else:
        return {
            "success": False, "message": "Something went wrong on our end. Try again later."
        }
    
def main():
    new_user = {
        "username": "c13u",
        "email_address": "unique1@gmail.com",
        "password": "this_is_long_enough",
    }
    print(register_user(new_user))  

if __name__ == "__main__":
    main()    
    
