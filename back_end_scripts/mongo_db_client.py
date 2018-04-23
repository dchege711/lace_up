"""

"""

#_______________________________________________________________________________

import os
from pymongo import MongoClient, IndexModel, TEXT, DESCENDING, HASHED
from pprint import pprint
from bson.son import SON

#_______________________________________________________________________________

indexes = {
	"attendee_details": [
		("Email", HASHED), 
	],
	"trip_details": [
		("origin", TEXT), ("departure_date", DESCENDING),
		("departure_time", DESCENDING), ("seats_available", DESCENDING)
	]
}

class tiger_rides_db():
	
	def __init__(self, collection_name):
		self.client = MongoClient(os.environ["TIGER_RIDES_MONGO_URI"])
		self.db = self.client["dgitau_orf401"]
		self.collection_name = collection_name
		self.collection = self.db[collection_name]
		
	def _initialize(self):
		self.collection.drop_indexes()
		for index in indexes[self.collection_name]:
			self.collection.create_index([index])
		
	def create(self, doc):
		return self.collection.insert_one(doc)
	
	def update(self, filter_key, key_value_pairs):
		return self.collection.update_one(
			filter_key, {"$set": key_value_pairs}
		)
			
		
	def get_next_id(self):
		metadata = self.collection.find_one({"document_type": "metadata"})
		next_id = metadata["next_id"]
		self.update(
			{"_id": metadata["_id"]},
			{"next_id": next_id + 1}
		)
		return next_id
		
	def read(self, query):
		return self.collection.find_one(filter=query)
	
	def delete(self, query_filter):
		return self.collection.delete_one(query_filter)
		
def main():
	tiger_rides = tiger_rides_db("attendee_details")
	# tiger_rides._initialize()
	# tiger_rides.create({
	# 	"email": "nothing@gmail.com",
	# 	"first_name": "Kaboom",
	# 	"last_name": "Psyche",
	# 	"origin": "Nashville",
	# 	"leaving_date": "01-01-2018",
	# 	"leaving_time": "12:34PM",
	# 	"has_car": "no",
	# 	"password": "lets_save_passwords_in_plain_text"
	# })
	print(tiger_rides.get_next_id())
	
	
	

if __name__ == "__main__":
	main()
