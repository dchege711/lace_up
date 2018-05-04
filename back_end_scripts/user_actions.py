"""
user_actions.py

Supports user related actions such as `is_in_db`, `get_user`,
`get_games`, `update_user`, `update_user_append`, 
`delete_user`, `register_user`.

"""

import secrets
import string
from random import choice
import bcrypt
from datetime import datetime, timedelta
from mongo_db_client import sport_together_db
import game_actions

users_db = sport_together_db("sport_together_user_account_info")
games_db = sport_together_db("sport_together_game_details")
sessions_db = sport_together_db("session_info")

# Instance variables for authentication purposes with bcrypt
desired_key_bytes = 32
salt_rounds = 12
pbkdf_rounds = 100

def is_in_db(key_val_pair):
    """
    @param `key_val_pair` (JSON): A key-value pair that might be
    associated with an account in the database.

    @return `True` if the key-value pair exists in the database.
    """
    if users_db.read(key_val_pair) is not None:
        return True
    else:
        return False

def register_user(new_user_info):
    """
    Register a new user. 

    @param `new_user_info` (JSON): The registration details of the
    new user. Expected keys: `email_address`, `password`.

    @returns (JSON): Expected keys: `success`, `message`.

    """

    submitted_keys = set(new_user_info.keys())
    mandatory_keys = set(game_actions.supported_games)
    for key in ("email_address", "password", "first_name", "last_name", "university"):
        mandatory_keys.add(key)

    for expected_key in mandatory_keys:
        if expected_key not in submitted_keys:
            raise KeyError(
                "Did not find `", expected_key, "` as a key in `game_info`"
            )

    # We won't allow accounts that have more than one email address
    if is_in_db({"email_address": new_user_info["email_address"]}):
        return {
            "success": False,
            "message": "That email address has already been taken."
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
        password=new_user_info["password"].encode("utf-8"),
        salt=salt, desired_key_bytes=desired_key_bytes, rounds=pbkdf_rounds
    )
    validation_url = secrets.token_urlsafe(32)

    new_user_account_info = {
        "email_address": new_user_info["email_address"],
        "first_name": new_user_info["first_name"], 
        "last_name": new_user_info["last_name"],
        "username": username, "salt": salt, "hash": hashed_pw,
        "validation_url": validation_url, "already_validated": False,
        "signup_time": datetime.today().timestamp(), 
        "university": new_user_info["university"],
        "user_id": new_user_id, "games_joined": [],
        "games_owned": [], "orphaned_games": []
    }

    for supported_game in game_actions.supported_games:
        new_user_account_info[supported_game] = new_user_info[supported_game]

    insert_results = users_db.create(new_user_account_info)

    if insert_results.inserted_id is not None:
        return {
            "success": True, "message": new_user_id
        }
    else:
        return {
            "success": False, "message": "500 Server Error."
        }

def ninja_update_user_append(new_user_info):
    """
    Some updates don't require signing in and authenticating a user.

    """
    assert "user_id" in new_user_info, "`user_id` should have been specified"
    
    allowed_fields = {"orphaned_games", "already_validated"}

    user_id = new_user_info.pop("user_id")
    user_account_info = users_db.read({"user_id": user_id})

    for key in new_user_info:
        if key not in allowed_fields:
            return None
        try:
            user_account_info[key].append(new_user_info[key])

        except KeyError:
            user_account_info[key] = [new_user_info[key]]

        new_user_info[key] = user_account_info[key]

    update_result = users_db.update(
        {"user_id": user_id}, new_user_info
    )

    if update_result.modified_count == 1:
        return True

    else:
        return None
class sport_together_user():

    def __init__(self, identifier_key_val_pair, password):
        """
        Get the account associated with the specified unique identifier.

        @param `identifier_key_val_pair` (JSON): A key value pair associated
        with only one account. Expects either `email_address` or `username` as
        the key.

        @param `password` (str): The password associated with the account.

        """
        # Store the identifier for later references
        self.identifier_key_val_pair = identifier_key_val_pair

        # Attempt to authenticate and load the user details
        self.account = self._authenticate_user(password)

        # If successfully authenticated, assign a session ID for further
        # session requests without requiring a password.
        if self.account is not None:
            session_token = self._create_session_token()
            for key in session_token:
                self.account[key] = session_token[key]
    
    def _authenticate_user(self, password):
        """
        Authenticate a user who is trying to log in.

        @param `submitted_credentials` (JSON): Expected keys: 
        `email_address_or_username`, `password`.

        @return (bool): (JSON) if user was successfully authenticated,
        `NoneType` otherwise.

        """
        account_info = users_db.read(self.identifier_key_val_pair)

        if account_info is None:
            return None

        calculated_hash = bcrypt.kdf(
            password=password.encode("utf-8"), rounds=pbkdf_rounds,
            salt=account_info["salt"], desired_key_bytes=desired_key_bytes
        )

        if calculated_hash == account_info["hash"]:
            return account_info
        else:
            return None

    def _refresh(self):
        """
        Reload the user account details from the database.

        """
        if self.account == None:
            return None

        self.account = users_db.read(self.identifier_key_val_pair)

    def get_games(self):
        """
        Fetch all the games that the user has created or joined.

        @returns: (JSON): Contains the keys `games_owned` and
        `games_joined`, `orphaned_games`.

        """
        
        if self.account is None:
            return {
                "games_owned": None, 
                "games_joined": None, "orphaned_games": None
            }
        
        return {
            "games_owned": game_actions.get_games(self.account["games_owned"]),
            "games_joined": game_actions.get_games(self.account["games_joined"]),
            "orphaned_games": game_actions.get_games(self.account["orphaned_games"])
        }

    def _create_session_token(self):
        """
        Create a token for use in the current user session. This token expires
        after a set time.

        @returns (JSON): Empty JSON if user is not authenticated. Otherwise, 
        the keys include `token`, `expiry` and `user_id`.

        """
        if self.account is None:
            return {}

        session_token = {
            "session_token": secrets.token_urlsafe(nbytes=32),
            "expiry": datetime.now().timestamp() + 5 * 3600,
            "user_id": self.account["user_id"]
        }

        sessions_db.create(session_token)
        return session_token


    def return_user_info(self, keys_to_use=None):
        """
        Return relevant account information. 

        @param `keys_to_use` (Iterable): The keys (and their associated
        values) that need to be returned. Useful for trimming the amount 
        of information sent back and forth.

        @return (JSON) if successful, `None` if unsuccessful.

        """

        if self.account is None:
            return None

        if keys_to_use == None:
            keys_to_use = [
                "user_id", "first_name", "games_joined", "games_owned", 
                "orphaned_games", "session_token"
            ]
        
        user_info_payload = {}
        for key in keys_to_use:
            user_info_payload[key] = self.account[key]

        return user_info_payload

    def delete_user(self):
        """
        Delete the user's account from Sport Together.

        @returns (bool): `True` if the user's account was deleted, 
        `False` otherwise

        """
        if self.account is None:
            return False

        for game_id in self.account["games_joined"]:
            self.withdraw_from_game(game_id)

        for game_id in self.account["games_owned"]:
            self.withdraw_from_game(game_id)
        
        delete_result = users_db.delete(self.identifier_key_val_pair)

        if delete_result["user_id"] == self.account["user_id"]:
            self._refresh()
            return True
        else:
            return False

    def update_user_append(self, new_user_info):
        """
        Append new information to existing information on the user's
        profile.

        @param `new_user_info` (JSON): A JSON object with the info to
        be appended. `user_id` must be one of the keys in the JSON

        @return (JSON): Contains the key `user_info` that is `None`
        only if the update wasn't successful.

        """
        assert "user_id" in new_user_info, "`user_id` should have been specified"
        assert new_user_info["user_id"] == self.account["user_id"]
        
        new_user_info.pop("user_id")

        for key in new_user_info:
            # This is an inplace function!
            try:
                self.account[key].append(new_user_info[key])

            except KeyError:
                self.account[key] = [new_user_info[key]]

            new_user_info[key] = self.account[key]

        update_result = users_db.update(
            self.identifier_key_val_pair, new_user_info
        )

        if update_result.modified_count == 1:
            self._refresh()
            return self.return_user_info()

        else:
            return None

    def update_user(self, new_user_info):
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
        assert new_user_info["user_id"] == self.account["user_id"]

        new_user_info.pop("user_id")
        result = users_db.update(
            self.identifier_key_val_pair, new_user_info
        )
        if result.modified_count == 1:
            self._refresh()
            return self.return_user_info()
        else:
            return None  

    def add_game(self, game_info):
        """
        Add a game to the database of games and associate it with this
        user.

        param(s):
        game_info (dict)    Expected keys: type, location, "time"

        return(s):
        (int) The id of the inserted game, or NoneType if the 
        game wasn't successfully inserted into the database.

        """

        if self.account is None:
            return None

        for expected_key in ("type", "location", "time", "date"):
            if expected_key not in game_info.keys():
                raise KeyError(
                    "".join([
                        "Did not find '", expected_key, "' as a key in `game_info`"
                    ])
                )

        # Get a unique ID for each game. This ID should be different from database ID
        alphabet = string.ascii_uppercase + string.digits
        while True:
            game_id = "".join(choice(alphabet) for i in range(12))
            if games_db.read({"game_id": game_id}) is None:
                break

        game_info["game_id"] = game_id
        game_info["game_owner_id"] = self.account["user_id"]
        game_info["game_owner_first_name"] = self.account["first_name"]
        game_info["html_version"] = game_actions.convert_game_info_to_html(game_info)

        insert_results = games_db.create(game_info)

        new_user_info = {
            "user_id": self.account["user_id"],
            "games_owned": game_id
        }

        self.update_user_append(new_user_info)

        if insert_results.inserted_id is not None:
            return game_id
        else:
            return None
    
    def join_existing_game(self, game_id):
        """
        Join an already existing game.

        @param `game_id` (str): The ID of the game to join.

        @return (bool) `True` if successful, `False` otherwise.

        """
        if self.account is None:
            return False

        self.update_user_append({
            "user_id": self.account["user_id"],
            "games_joined": game_id
        })

        game_actions.update_game_append({
            "game_id": game_id,
            "game_attendees": self.account["user_id"],
            "game_attendees_first_names": self.account["first_name"]
        })

    def withdraw_from_game(self, game_id):
        """
        Remove the user's participation in the given game.

        @param `game_id` (str): The ID of the game.

        @param `user_id` (str): The ID of the user.

        """
        game_to_modify = games_db.read({"game_id": game_id})

        if game_to_modify is None:
            return False

        user_id = self.account["user_id"]
        if user_id in game_to_modify["game_attendees"]:
            game_to_modify["game_attendees"].remove(user_id)

        if user_id == game_to_modify["game_owner_id"]:
            game_to_modify["game_owner_id"] = ""

            for affected_user_id in game_to_modify["game_attendees"]:
                ninja_update_user_append({
                    "user_id": affected_user_id,
                    "orphaned_games": game_id
                })

        return True

def main():
    new_user = {
        "username": "c13u",
        "email_address": "unique1@gmail.com",
        "password": "this_is_long_enough",
    }
    print(register_user(new_user))  

if __name__ == "__main__":
    main()    
    
