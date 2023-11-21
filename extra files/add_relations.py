import pandas as pd
import csv
from pymongo import MongoClient

# MongoDB connection settings
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["ecommerce"]  # Replace with your MongoDB database name
collection = db["doc1"]  # Replace with your MongoDB collection name

# Specify the path to your CSV file
df = pd.read_csv("erd-schema_1.csv")
# print(df.head())
csv_file_path = "erd-schema_datatype.csv"  # Replace with the path to your CSV file

# Convert DataFrame to a list of dictionaries (one dictionary per row)
data = df.to_dict(orient="records")

# Delete all collections from database except default collection "doc1"
collection_to_exclude = "doc1"
collection_names = db.list_collection_names()
for collection_name in collection_names:
    if collection_name != collection_to_exclude:
        db[collection_name].drop()

# card1 = []
# for value in df['Card1']:
#     card1.append(value)
# card2 = []
# for value in df['Card2']:
#     card2.append(value)

entity_attributes = {} # empty dictionary to store attribute and datatype for each entity

# Open the CSV file
with open(csv_file_path, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)  # Skip the header row

    for row in csv_reader:
        entity_name, attribute_name, data_type, *_ = row

        # Create a new collection for the entity if it doesn't exist
        if entity_name not in db.list_collection_names():
            db.create_collection(entity_name)
            entity_attributes[entity_name] = []
        # Add the attribute name and data type to the entity's attribute list
        entity_attributes[entity_name].append({attribute_name: data_type})

for index, row in df.iterrows():
    entity1 = row['Entity1']
    entity2 = row['Entity2']
    column1_value = row['Card1']
    column2_value = row['Card2']
    
    if column1_value == 1 and column2_value > 500: # one-to-many as well as one-to-squillion
        # print("reference")
        # print(entity2 + "_id")
        entity_attributes[entity1].append({"ref_"+entity2+"_id": "array"})
    elif column1_value == 1 and column2_value <= 500:
        print("embed")
    elif column1_value > 1 and column2_value == 1:
        # print("reference")
        entity_attributes[entity2].append({"ref_"+entity1+"_id": "array"})
    elif column1_value > 1 and column2_value > 1:
        # print("reference or new document")
        entity_attributes[entity1].append({"ref_"+entity2+"_id": "array"})
        entity_attributes[entity2].append({"ref_"+entity1+"_id": "array"})

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