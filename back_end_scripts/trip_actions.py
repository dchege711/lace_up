from mongo_db_client import tiger_rides_db
import user_actions

trips_db = tiger_rides_db("trip_details")

def add_trip(trip_info):
    """
    Add a trip to the database of trips.

    param(s):
    trip_info (dict)    Expected keys: origin, destination, 
                        departure_time, seats_available

    return(s):
    (int) The id of the the inserted trip, or NoneType if the 
    trip wasn't successfully inserted into the database.

    """
    new_trip_id = trips_db.get_next_id()
    trip_info["trip_id"] = new_trip_id
    trip_info["html_version"] = _convert_trip_info_to_html_row(trip_info)
    
    insert_results = trips_db.create(trip_info)
    new_user_info = {
        "user_id": trip_info["trip_owner"],
        "trips_owned": new_trip_id
    }
    user_actions.update_user_append(new_user_info)
    
    if insert_results.inserted_id is not None:
        return new_trip_id
    else:
        return None
    
def _convert_trip_info_to_html_row(trip_info):
    """

    """
    return ''.join([
        "<tr><td>#", str(trip_info["trip_id"]), "</td>",
        "<td>", trip_info["origin"], "</td>",
        "<td>", trip_info["destination"], "</td>",
        "<td>", trip_info["departure_date"], "</td>", 
        "<td>", trip_info["departure_time"], "</td>", 
        "<td>", str(trip_info["seats_available"]), "</td>",
        "<td><button class='w3-btn w3-hover-white' onClick='return editTrip(", 
        str(trip_info["trip_id"]), 
        ")'> <b><i class='fa fa-pencil fa-fw'></i></b></button></td><tr>"
    ])
    
def get_trips(trip_ids):
    relevant_trips = []
    for trip_id in trip_ids:
        trip = trips_db.read({"trip_id": trip_id})
        if trip is not None:
            trip.pop("_id", None)
            relevant_trips.append(trip)
    return relevant_trips

def update_trip_append(trip_info):
    trip_id = trip_info.pop("trip_id", None)
    query = {"trip_id": trip_id}
    trip = trips_db.read(query)
    
    for key in trip_info:
        trip[key].append(trip_info[key])
        trip_info[key] = trip[key]
        
    trip_info["trip_id"] = trip_id 
    return update_trip(trip_info)
        

def update_trip(new_trip_info):
    query = {"trip_id": new_trip_info["trip_id"]}    
    trip_to_modify = trips_db.read(query)
    for key in new_trip_info:
        trip_to_modify[key] = new_trip_info[key]
    trip_to_modify["html_version"] = _convert_trip_info_to_html_row(trip_to_modify)
    
    update_results = {}
    result = trips_db.update(query, trip_to_modify)
    
    if result.modified_count == 1:
        update_results["trip_info"] = new_trip_info
    else:
        update_results["trip_info"] = False
            
    return update_results

def main():    
    test_trip = {
        'origin': 'Las Vegas', 
        'destination': 'Princeton University', 
        'departure_date': '2018-03-15', 
        'departure_time': '14:00', 
        'seats_available': '0', 
        'trip_id': 4
    }
    # print(_convert_trip_info_to_html_row(test_trip))
    test_trip["seats_available"] = 11
    print(update_trip(test_trip))

if __name__ == "__main__":
    main()
        
