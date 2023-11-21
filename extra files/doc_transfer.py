import pymongo
from bson import ObjectId

# Connect to MongoDB (assuming it's running locally)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]  # Replace with your database name

# Define the source and target collections
source_collection = db["doc-source"]  # Replace with the source collection name
target_collection = db["doc-target"]  # Replace with the target collection name

# Define the criteria to identify the document you want to transfer (e.g., by _id)
document_criteria = {"name": "Dhwani"}  # Replace with the document's _id

# Find the document in the source collection
document_to_transfer = source_collection.find_one(document_criteria)

# Check if the document was found
if document_to_transfer:
    # Insert the document into the target collection
    target_collection.insert_one(document_to_transfer)
    
    # Delete the document from the source collection
    source_collection.delete_one(document_criteria)
    
    print("Document transferred and deleted successfully.")
else:
    print("No document matched the criteria.")

# Close the MongoDB connection
client.close()