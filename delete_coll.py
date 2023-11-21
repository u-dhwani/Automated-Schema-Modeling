import pandas as pd
import csv
from pymongo import MongoClient
from pymongo import InsertOne

# MongoDB connection settings
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["ecommerce"]  # Replace with your MongoDB database name
collection = db["doc1"]  # Replace with your MongoDB collection name

# Delete all collections from the database except the default collection "doc1"
collection_to_exclude = "doc1"
collection_names = db.list_collection_names()
for collection_name in collection_names:
    if collection_name != collection_to_exclude:
        db[collection_name].drop()