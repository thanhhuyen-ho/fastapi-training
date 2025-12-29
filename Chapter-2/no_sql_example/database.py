from pymongo import MongoClient

client = MongoClient()

database = client.mydatabase

user_collection = database["users"]