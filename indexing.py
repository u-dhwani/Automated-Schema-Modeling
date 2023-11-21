from pymongo import MongoClient, ASCENDING

# Replace with your MongoDB connection string
client = MongoClient("mongodb://localhost:27017/")
db = client["db2"]
collection = db["order_item"]

attr = input("Enter field: ")
val = input("Enter value: ")
collection.create_index([(attr, ASCENDING)])
query = {attr: val}

# Use the find method with the query
results = collection.find(query)

# Print the results
for doc in results:
    print(doc)