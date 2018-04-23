"""
mongo_db_client.py

A wrapper around the MongoDB database hosting game and account
information.

"""

#_______________________________________________________________________________

import os
from pymongo import MongoClient, IndexModel, TEXT, DESCENDING, HASHED
from pprint import pprint
from bson.son import SON

#_______________________________________________________________________________

indexes = {
	"sport_together_user_account_info": [
		("user_id", HASHED), ("location", TEXT)
	],
	"sport_together_user_logins": [
		("email", HASHED), ("salt", TEXT)
	],
	"sport_together_game_details": [
		("location", TEXT), ("time", DESCENDING)
	]
}

class sport_together_db():
	"""
	A wrapper around the MongoDB database used for the Sport 
	Together application.

	"""
	
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
		
	def read(self, query):
		return self.collection.find_one(filter=query)
	
	def delete(self, query_filter):
		return self.collection.delete_one(query_filter)
		
def main():
	sport_together = sport_together_db("user_account_info")
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

if __name__ == "__main__":
	main()
