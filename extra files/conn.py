import pandas as pd
from pymongo import MongoClient

# Read the CSV file into a DataFrame
df = pd.read_csv("entity_attribute.csv")
# print(df)

# MongoDB connection settings
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["ecommerce"]  # Replace with your MongoDB database name
collection = db["doc1"]  # Replace with your MongoDB collection name

# Convert DataFrame to a list of dictionaries (one dictionary per row)
data = df.to_dict(orient="records")
# print(data)

# Delete all collections from database except default collection "doc1"
collection_to_exclude = "doc1"
collection_names = db.list_collection_names()
for collection_name in collection_names:
    if collection_name != collection_to_exclude:
        db[collection_name].drop()



# Get a set of entities
entity = set()
col_0 = []
for value in df['cart']:
    col_0.append(value)
    entity.add(value)
print("Entities:", entity)
col_1 = []
for value in df['price']:
    col_1.append(value)



# Create collections based on entities
key_value_dict = dict(zip(col_0, col_1))
data = {'key': col_0,
        'value': col_1}
df = pd.DataFrame(data)
# print(data)
result_dict = {}



for index, row in df.iterrows():
    collection_names = db.list_collection_names()
    key = row['key']
    value = row['value'] 
    # Check if the key is already in the dictionary
    if key in result_dict:
        result_dict[key].append(value)
        if key in collection_names:
            pass
        else:
            db.create_collection(key)
    else:
        result_dict[key] = [value]
# print(result_dict)



# Add fields to collections
is_present = set()
for index, row in df.iterrows():
    key = row['key']
    value = row['value']
    # Check if the key is already in the data dictionary
    if key in result_dict and key not in is_present:
        is_present.add(key)
        # Get the field names associated with the key
        field_names = result_dict[key]
        # Create a dictionary with the key-value pairs
        data_to_insert = {field_name: value for field_name in field_names}
        # Create or select the collection based on the key
        collection = db[key]
        # Insert the data as a document into the collection
        collection.insert_one(data_to_insert)
    else:
        pass



# Close the MongoDB connection
client.close()