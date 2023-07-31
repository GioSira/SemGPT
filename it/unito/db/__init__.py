from pymongo import MongoClient

__USER = "laura"
__PASSWORD = "L9W4DElh8nDyOOY1"
__DBNAME = "Semagram"

CONNECTION_STRING = f"mongodb+srv://{__USER}:{__PASSWORD}@csemagram.a4kafks.mongodb.net/{__DBNAME}?retryWrites=true&w=majority"

client = MongoClient(CONNECTION_STRING)

dbname = client['semagram']
sem_collection = dbname["concepts"]
category_collection = dbname['categories']
