"""
game_actions.py

Supports game related actions such as `add_game`, `get_games`,
`update_game_append`, `update_game`, `remove_user_from_game`.

"""

import secrets
import string
from random import choice

from mongo_db_client import sport_together_db
import user_actions

games_db = sport_together_db("sport_together_game_details")
supported_games = {
    "tennis", "frisbee", "soccer", "running", "basketball"
}
def filter_local_games(all_local_games):
    """
    returns games that are local for the logged in user.

    Sample payload:

        {
            "location": "princeton",
            "type": "soccer"
        }
    """
    results = []
    for game in games_db.scan(all_local_games):
        game.pop("_id", None)
        results.append(game)

    return results


def check_mandatory_fields(game_info):
    """
    @raises `KeyError` exception if `game_info` doesn't have
    enough information to create a game.

    """
    for expected_key in ("type", "location", "game_owner_id", "game_owner_first_name"):
        if expected_key not in game_info.keys():
            raise KeyError(
                "Did not find `", expected_key, "` as a key in `game_info`"
            )

def get_games(game_ids):
    """
    Get all the games using the supplied game IDs. Useful say when fetching
    all the games that a user is a part of.

    @param `game_ids` (Iterable): The IDs of the games to fetch.

    @returns (List): A list of JSON objects, each representing a game.

    """
    relevant_games = []
    for game_id in game_ids:
        game = games_db.read({"game_id": game_id})
        if game is not None:
            game.pop("_id", None)
            relevant_games.append(game)
    return relevant_games

def update_game_append(new_game_info):
    """
    Update specific fields in the game object. Useful when adding participants
    in an existing game. Prevents overwriting of existing information.

    @param `new_game_info` (JSON): key-value pairs of the info that needs to
    be updated. The `game_id` key is mandatory.

    """

    if "game_id" not in new_game_info.keys():
        raise KeyError("`game_id` should be specified in the input.")

    game_id = new_game_info.pop("game_id", None)
    query = {"game_id": game_id}
    game_to_modify = games_db.read(query)

    for key in new_game_info:
        try:
            game_to_modify[key].append(new_game_info[key])
        except KeyError:
            game_to_modify[key] = [new_game_info[key]]
    
    return _helper_write_changes_to_db(game_to_modify)

def update_game(new_game_info):
    """
    Update specific fields in the game object. Useful when adding participants
    in an existing game.

    @param `game_info` (JSON): key-value pairs of the info that needs to be
    updated. The `game_id` key is mandatory.

    @warning: If the key already exists in the game, the associated value will
    be overwritten!

    """

    if "game_id" not in new_game_info.keys():
        raise KeyError("`game_id` should be specified in the input.")

    game_to_modify = games_db.read({"game_id": new_game_info["game_id"]})
    for key in new_game_info:
        game_to_modify[key] = new_game_info[key]

    return _helper_write_changes_to_db(game_to_modify)

def _helper_write_changes_to_db(new_game_info):
    """

    Helper method for writing game information to the database.
    Used to avoid code duplication in `update_game` and
    `update_game_append`.

    """
    update_results = {}
    result = games_db.update(
        {
            "game_id": new_game_info["game_id"]
        }, new_game_info
    )

    if result.modified_count == 1:
        update_results["game_info"] = new_game_info
    else:
        update_results["game_info"] = False

    return update_results
