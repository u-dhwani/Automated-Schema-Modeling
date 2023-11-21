import pandas as pd
import csv
from pymongo import MongoClient

# MongoDB connection settings
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["ecommerce"]  # Replace with your MongoDB database name

# Specify the path to your CSV file
csv_file_path = "erd-schema_datatype.csv"  # Replace with the path to your CSV file

# Delete all collections from database except default collection "doc1"
collection_to_exclude = "doc1"
collection_names = db.list_collection_names()
for collection_name in collection_names:
    if collection_name != collection_to_exclude:
        db[collection_name].drop()

# Create a dictionary to store attribute data for each entity
entity_attributes = {}

# Open the CSV file
with open(csv_file_path, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)  # Skip the header row

    for row in csv_reader:
        entity_name, attribute_name, data_type, a, b, c, d, e = row

        # Create a new collection for the entity if it doesn't exist
        if entity_name not in db.list_collection_names():
            db.create_collection(entity_name)
            entity_attributes[entity_name] = []
        # Add the attribute name and data type to the entity's attribute list
        entity_attributes[entity_name].append({attribute_name: data_type})

    for entity_name, attributes in entity_attributes.items():
        collection = db[entity_name]
        
        # Combine all inner dictionaries into a single document
        combined_document = {}
        for inner_dict in attributes:
            combined_document.update(inner_dict)
        
        # Insert the combined document into the collection
        collection.insert_one(combined_document)

# Close the MongoDB connection
client.close()
