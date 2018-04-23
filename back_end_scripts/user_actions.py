from mongo_db_client import tiger_rides_db
import trip_actions

users_db = tiger_rides_db("attendee_details")

def is_in_db(key_val_pair):
    if users_db.read(key_val_pair) is not None:
        return True 
    else:
        return False

def get_trips(user_id):
    
    user_profile = users_db.read({"user_id": user_id})
    trips = {}
    
    if user_profile is None:
        return trips
    
    trips["trips_owned"] = user_profile["trips_owned"]
    trips["trips_joined"] = user_profile["trips_joined"]
    
    return trips

def update_user_append(user_info):
    user_id = user_info.pop("user_id", None)
    query = {"user_id": user_id}
    user = users_db.read(query)
    
    for key in user_info:
        user[key].append(user_info[key]) # This is an inplace function!
        user_info[key] = user[key]
        
    user_info["user_id"] = user_id 
    return update_user(user_info)

def update_user(new_user_info):
    query = {"user_id": new_user_info["user_id"]}
    update_results = {}
    
    result = users_db.update(query, new_user_info)
    if result.modified_count == 1:
        update_results["user_info"] = new_user_info
    else:
        update_results["user_info"] = False
            
    return update_results    
     

def get_user(key_val_pairs):
    return users_db.read(key_val_pairs)

def delete_user(user_id):
    return users_db.delete({"user_id": user_id})

def register_user(user_details):
    new_user_id = users_db.get_next_id()
    user_details["user_id"] = new_user_id
    user_details["trips_joined"] = []
    user_details["trips_owned"] = []
    insert_results = users_db.create(user_details)
    
    trip_info_in_registration = [
        "origin", "departure_date", "departure_time", "seats_available", "destination"
    ]
    trip_info = {}
    for key in trip_info_in_registration:
        value = user_details.pop(key, None)
        if value != "":
            trip_info[key] = value
    if len(trip_info) != 0:
        trip_info["trip_owner"] = new_user_id
        trip_actions.add_trip(trip_info)
    
    try:
        user_internal_id = insert_results.inserted_id
        return True, new_user_id 
    except Exception as e:
        print(e)
        return False, None
    
def main():
    new_user = {
        "first_name": "Test User",
        "last_name": "Why",
        "email_address": "unique1@gmail.com",
        "password": "this_is_long_enough",
        "origin": "Naples New",
        "destination": "Silicy",
        "departure_date": "2018-02-27",
        "departure_time": "12:00",
        "seats_available": 12
    }
    success, user_id = register_user(new_user)
    

if __name__ == "__main__":
    main()    
    
