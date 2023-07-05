import pymongo
from utils import constants as constants

def get_mongo_db(database_name):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["test-mongo"]
        database = db[database_name]
        return database
        print('Mongo connected')
    except:
        print('Mongo not connected')

def clean_mongo_data(database_name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["test-mongo"]
    database = db[database_name]
    database.drop()
    print('Mongo data cleaned')