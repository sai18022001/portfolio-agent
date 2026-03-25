from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client["portfolio_agent"]

db["test"].insert_one({"message": "MongoDB is working"})

result = db["test"].find_one({"message": "MongoDB is working"})
print(result)
db["test"].drop()
print("MongoDB connction wotking")