from flask import Flask, render_template, request, jsonify, render_template, send_file, Response
import io
import pandas as pd
import csv
from pymongo import MongoClient, ASCENDING
from gridfs import GridFS
from bson import json_util
import json

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("index.html")

# MongoDB connection settings
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["database9"]  # Replace with your MongoDB database name

@app.route('/process', methods=['POST'])
def process_files():
    # Get the uploaded files
    entity_attr_file = request.files['entity-attr']
    cardinality_file = request.files['cardinality']

    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        db[collection_name].drop()

    entity_attributes = {}

    # Process entity_attr_file
    with open(entity_attr_file.filename, 'r') as entity_attr_csv_file:
        csv_reader = csv.DictReader(entity_attr_csv_file)
        for row in csv_reader:
            entity_name = row['EntityName']
            attribute_name = row['AttributeName']
            data_type = row['DataType']
            
            # Check if the entity already exists in the dictionary
            if entity_name in entity_attributes:
                entity_attributes[entity_name].append({attribute_name: data_type})
            else:
                # Create a new entry for the entity
                entity_attributes[entity_name] = [{attribute_name: data_type}]

    # Process cardinality_file using pandas
    cardinality_df = pd.read_csv(cardinality_file)
    for index, row in cardinality_df.iterrows():
        entity1 = row['Entity1']
        entity2 = row['Entity2']
        column1_value = row['Card1']
        column2_value = row['Card2']

        if column1_value == 1 and column2_value > 500: # one-to-many as well as one-to-squillion
            # print("reference")
            entity_attributes[entity1].append({"ref_"+entity2+"_id": "array"})
        
        elif column1_value == 1 and column2_value <= 500: 
            # print("embed")
            entity_attributes[entity1].append({entity2: entity_attributes[entity2]})

        elif column1_value > 1 and column2_value == 1:
            # print("reference")
            entity_attributes[entity2].append({"ref_"+entity1+"_id": "array"})
        
        elif column1_value > 1 and column2_value > 1:
            # print("reference or new document")
            entity_attributes[entity1].append({"ref_"+entity2+"_id": "array"})
            entity_attributes[entity2].append({"ref_"+entity1+"_id": "array"})

    # Insert data into MongoDB
    for entity_name, attributes in entity_attributes.items():
        collection = db[entity_name]
        
        # Combine all inner dictionaries into a single document
        combined_document = {}
        for inner_dict in attributes:
            combined_document.update(inner_dict)
        
        # Insert the combined document into the collection
        collection.insert_one(combined_document)

    collections = db.list_collection_names()
    return render_template('collections.html', collections=collections)

# Route to retrieve and display documents of a selected collection in JSON format
@app.route('/collection/<collection_name>')
def view_collection(collection_name):
    collection = db[collection_name]
    documents = list(collection.find({}))
    return render_template('doc.html', collection_name=collection_name, documents=documents)

@app.route('/query', methods=['POST', 'GET'])
def query():
    access_path = request.form.get('access-path')

    # Query MongoDB to find which collection embeds the accessed collection
    result = find_embedded_collection(access_path)
    collection=db.list_collection_names()
    return render_template('collections.html', collections=collection)

def find_embedded_collection(access_path):
    collection_documents = {}
    entity_attr_file = request.files['entity-attr']
    cardinality_file = request.files['cardinality']

    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        db[collection_name].drop()

    entity_attributes = {}

    # Process entity_attr_file
    with open(entity_attr_file.filename, 'r') as entity_attr_csv_file:
        csv_reader = csv.DictReader(entity_attr_csv_file)
        # next(csv_reader)
            
        for s_row in csv_reader:
            entity_name, attribute_name, data_type, *_ = s_row
            entity_name = s_row['EntityName']
            attribute_name = s_row['AttributeName']
            data_type = s_row['DataType']
            
            # Check if the entity already exists in the dictionary
            if entity_name in entity_attributes:
                entity_attributes[entity_name].append({attribute_name: data_type})
            else:
                # Create a new entry for the entity
                entity_attributes[entity_name] = [{attribute_name: data_type}]

    # Process cardinality_file using pandas
    df = pd.read_csv(cardinality_file)
    with open(cardinality_file.filename, newline='') as cardfile:
        csv_reader = csv.reader(cardfile)
        next(csv_reader)  # Skip the header row

        for c_row in csv_reader:
            entity1, entity2, rel, card1, card2 = c_row

    values = access_path.split('/')
    # print(values)
    attr = ""
    val = ""
    embedding_coll = []
    last_ele = values[-1]  # Extract the last part after splitting by '/'
    if '?' in last_ele:
        last_parts = last_ele.split('?')
        if '=' in last_parts[1]:
            attr = last_parts[1].split('=')[0]
            if type(val) == 'int':
                val = int(last_parts[1].split('=')[1])
            else:
                val = last_parts[1].split('=')[1]
        elif '>' in last_parts[1]:
            attr = last_parts[1].split('>')[0]
            if type(val) == 'int':
                val = int(last_parts[1].split('>')[1])
            else:
                val = last_parts[1].split('>')[1]
        elif '<' in last_parts[1]:
            attr = last_parts[1].split('<')[0]
            if type(val) == 'int':
                val = int(last_parts[1].split('<')[1])
            else:
                val = last_parts[1].split('<')[1]
        elif '>=' in last_parts[1]:
            attr = last_parts[1].split('>=')[0]
            if type(val) == 'int':
                val = int(last_parts[1].split('>=')[1])
            else:
                val = last_parts[1].split('>=')[1]
        elif '<=' in last_parts[1]:
            attr = last_parts[1].split('<=')[0]
            if type(val) == 'int':
                val = int(last_parts[1].split('<=')[1])
            else:
                val = last_parts[1].split('<=')[1]
        elif '!=' in last_parts[1]:
            attr = last_parts[1].split('!=')[0]
            if type(val) == 'int':
                val = int(last_parts[1].split('!=')[1])
            else:
                val = last_parts[1].split('!=')[1]
        else:
            attr = last_parts[1]
        values[-1] = last_parts[0]  # Replace the last element with the value before the '?'

        print(values)
        print(attr, val)
        print(values[-1])
        if attr is not None and val is not None:
            db[values[-1]].create_index([(attr, ASCENDING)])
            query = {attr: val}
            results = db[values[-1]].find(query)
        elif attr is None and val is None:
            db[values[-1]].create_index([(attr, ASCENDING)])
            results = db[values[-1]].find({attr: {"$exists": True}})
        print(results)
        print(results.explain())

    # print(values)

    for i in range(len(values)-2, -1, -1):
        curr_element = values[i]
        next_element = values[i+1]
        # print(curr_element, next_element)
        matching_row = df[(df['Entity1'].str.lower() == curr_element) & (df['Entity2'].str.lower() == next_element)]
        rev_match = df[(df['Entity2'].str.lower() == curr_element) & (df['Entity1'].str.lower() == next_element)]

        if not matching_row.empty:

            column1_value = matching_row['Card1'].values[0]
            column2_value = matching_row['Card2'].values[0]

            if column1_value == 1 and column2_value > 500: # one-to-many as well as one-to-squillion
                entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
            elif column1_value == 1 and column2_value <= 500:
                entity_attributes[curr_element].append({next_element: entity_attributes[next_element]})
                embedding_coll.append(next_element)
            elif column1_value > 1 and column2_value == 1:
                entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})
            elif column1_value > 1 and column2_value > 1:
                entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})

        if not rev_match.empty:

            column1_value = rev_match['Card2'].values[0]
            column2_value = rev_match['Card1'].values[0]

            if column1_value == 1 and column2_value > 500: # one-to-many as well as one-to-squillion
                entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
            elif column1_value == 1 and column2_value <= 500: # one-to-one
                entity_attributes[curr_element].append({next_element: entity_attributes[next_element]})
                embedding_coll.append(next_element)
            elif column1_value > 1 and column2_value == 1:
                entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})
            elif column1_value > 1 and column2_value > 1:
                entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})

    for entity_name, attributes in entity_attributes.items():
            collection = db[entity_name]
            
            # Combine all inner dictionaries into a single document
            combined_document = {}
            for inner_dict in attributes:
                combined_document.update(inner_dict)
            
            # Insert the combined document into the collection
            collection.insert_one(combined_document)

    # print(embedding_coll)
    for coll in embedding_coll:
        db[coll].delete_many({})

    collection_data = {}
    file_name = "mongodb_data.txt"
    with open(file_name, "w") as file:
        pass
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        documents = collection.find()

        with open(file_name, "a") as text_file:
            for doc in documents:
                text_file.write(collection_name + ":\n\n")
                for field in doc:
                    text_file.write(str(field) + ":" + str(doc[field]) + "\n")
                text_file.write("\n\n")

    return send_file("mongodb_data.txt", as_attachment=True)


@app.route('/access_load', methods=['POST', 'GET'])
def mul_query():
    access_path_file = request.files['query-text'].filename

    # Query MongoDB to find which collection embeds the accessed collection
    result = find_final_collection(access_path_file)
    collection=db.list_collection_names()
    return render_template('collections.html', collections=collection)



def find_final_collection(access_path_file):
    collection_documents = {}
    entity_attr_file = request.files['entity-attr']
    cardinality_file = request.files['cardinality']

    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        db[collection_name].drop()

    entity_attributes = {}
    split_lines = []
    lists_dict = {}
    attr_val_pairs = {}

    with open(access_path_file, 'r') as file:
        for i, line in enumerate(file, start=1):
            values = line.strip().split('/')
            split_lines.append(values)
            list_name = f"list_{i}"
            lists_dict[list_name] = values

            attr = ""
            val = ""
            last_ele = values[-1]  # Extract the last part after splitting by '/'
            # print(last_ele)
            
            if '?' in last_ele:
                # print(last_ele)
                last_parts = last_ele.split('?')
                if '=' in last_parts[1]:
                    attr = last_parts[1].split('=')[0]
                    if type(val) == 'int':
                        val = int(last_parts[1].split('=')[1])
                    else:
                        val = last_parts[1].split('=')[1]
                elif '>' in last_parts[1]:
                    attr = last_parts[1].split('>')[0]
                    if type(val) == 'int':
                        val = int(last_parts[1].split('>')[1])
                    else:
                        val = last_parts[1].split('>')[1]
                elif '<' in last_parts[1]:
                    attr = last_parts[1].split('<')[0]
                    if type(val) == 'int':
                        val = int(last_parts[1].split('<')[1])
                    else:
                        val = last_parts[1].split('<')[1]
                elif '>=' in last_parts[1]:
                    attr = last_parts[1].split('>=')[0]
                    if type(val) == 'int':
                        val = int(last_parts[1].split('>=')[1])
                    else:
                        val = last_parts[1].split('>=')[1]
                elif '<=' in last_parts[1]:
                    attr = last_parts[1].split('<=')[0]
                    if type(val) == 'int':
                        val = int(last_parts[1].split('<=')[1])
                    else:
                        val = last_parts[1].split('<=')[1]
                elif '!=' in last_parts[1]:
                    attr = last_parts[1].split('!=')[0]
                    if type(val) == 'int':
                        val = int(last_parts[1].split('!=')[1])
                    else:
                        val = last_parts[1].split('!=')[1]
                else:
                    attr = last_parts[1]
                values[-1] = last_parts[0]  # Replace the last element with the value before the '?'

                # print(values)
                # print(attr, val)
                # print(values[-1])
                if attr is not None and val is not None:
                    db[values[-1]].create_index([(attr, ASCENDING)])
                    query = {attr: val}
                    results = db[values[-1]].find(query)
                    attr_val_pairs[values[-1]] = {attr: val}
                elif attr is not None and val is None:
                    db[values[-1]].create_index([(attr, ASCENDING)])
                    results = db[values[-1]].find({attr: {"$exists": True}})
                    attr_val_pairs[values[-1]] = {attr: {"$exists": True}}
                # print(results)
            # print(results.explain("executionStats"))

    num_lines = len(lists_dict)
    # print(lists_dict)

    # Process entity_attr_file
    with open(entity_attr_file.filename, 'r') as entity_attr_csv_file:
        csv_reader = csv.DictReader(entity_attr_csv_file)

        for s_row in csv_reader:
            entity_name, attribute_name, data_type, *_ = s_row
            entity_name = s_row['EntityName']
            attribute_name = s_row['AttributeName']
            data_type = s_row['DataType']
            
            # Check if the entity already exists in the dictionary
            if entity_name in entity_attributes:
                entity_attributes[entity_name].append({attribute_name: data_type})
            else:
                entity_attributes[entity_name] = [{attribute_name: data_type}] # Create a new entry for the entity

    # Process cardinality_file using pandas
    df = pd.read_csv(cardinality_file)
    with open(cardinality_file.filename, newline='') as cardfile:
        csv_reader = csv.reader(cardfile)
        next(csv_reader)  # Skip the header row

        for c_row in csv_reader:
            entity1, entity2, rel, card1, card2 = c_row

    # print(values)
    embedded_to =[]
    embedding_coll = []
    index_later = {}

    for list_name, values in lists_dict.items():
        for i in range(len(values)-2, -1, -1):
            curr_element = values[i]
            next_element = values[i+1]
            # print(curr_element, next_element)
            matching_row = df[(df['Entity1'].str.lower() == curr_element) & (df['Entity2'].str.lower() == next_element)]
            rev_match = df[(df['Entity2'].str.lower() == curr_element) & (df['Entity1'].str.lower() == next_element)]

            if not matching_row.empty:

                column1_value = matching_row['Card1'].values[0]
                column2_value = matching_row['Card2'].values[0]

                if column1_value == 1 and column2_value > 500: # one-to-many as well as one-to-squillion
                    if {"ref_"+next_element+"_id": "array"} not in entity_attributes[curr_element]:
                        entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                elif column1_value == 1 and column2_value <= 500:
                    if {next_element: entity_attributes[next_element]} not in entity_attributes[curr_element]:
                        entity_attributes[curr_element].append({next_element: entity_attributes[next_element]})
                        db[next_element].delete_many({})
                        embedded_to.append(curr_element)
                        embedding_coll.append(next_element)
                        if next_element in attr_val_pairs:
                            index_later[curr_element] = {next_element: attr_val_pairs[next_element]}
                elif column1_value > 1 and column2_value == 1:
                    if {"ref_"+curr_element+"_id": "array"} not in entity_attributes[next_element]:
                        entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})
                elif column1_value > 1 and column2_value > 1:
                    if {"ref_"+next_element+"_id": "array"} not in entity_attributes[curr_element]:
                        entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                    if {"ref_"+curr_element+"_id": "array"} not in entity_attributes[next_element]:
                        entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})
                    # entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                    # entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})

            if not rev_match.empty:

                column1_value = rev_match['Card2'].values[0]
                column2_value = rev_match['Card1'].values[0]

                if column1_value == 1 and column2_value > 500: # one-to-many as well as one-to-squillion
                    if {"ref_"+next_element+"_id": "array"} not in entity_attributes[curr_element]:
                        entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                elif column1_value == 1 and column2_value <= 500: # one-to-one
                    if {next_element: entity_attributes[next_element]} not in entity_attributes[curr_element]:
                        entity_attributes[curr_element].append({next_element: entity_attributes[next_element]})
                        db[next_element].delete_many({})
                        embedded_to.append(curr_element)
                        embedding_coll.append(next_element)
                        if next_element in attr_val_pairs:
                            index_later[curr_element] = {next_element: attr_val_pairs[next_element]}
                elif column1_value > 1 and column2_value == 1:
                    if {"ref_"+curr_element+"_id": "array"} not in entity_attributes[next_element]:
                        entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})
                elif column1_value > 1 and column2_value > 1:
                    if {"ref_"+next_element+"_id": "array"} not in entity_attributes[curr_element]:
                        entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                    if {"ref_"+curr_element+"_id": "array"} not in entity_attributes[next_element]:
                        entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})
                    # entity_attributes[curr_element].append({"ref_"+next_element+"_id": "array"})
                    # entity_attributes[next_element].append({"ref_"+curr_element+"_id": "array"})

    for entity_name, attributes in entity_attributes.items():
            collection = db[entity_name]
            
            # Combine all inner dictionaries into a single document
            combined_document = {}
            for inner_dict in attributes:
                combined_document.update(inner_dict)
            
            # Insert the combined document into the collection
            collection.insert_one(combined_document)
            # print(combined_document)
    
    # for coll in embedding_coll:
    #     db[coll].delete_many({})
    
    if index_later != {}:
        for entity_name, attributes in index_later.items():
            print(entity_name, attributes)
            for attr, val in attributes.items():
                for ind_attr, ind_val in val.items():
                    if ind_attr is not None and ind_val is not None:
                        db[entity_name].create_index([(ind_attr, ASCENDING)])
                        query = {ind_attr: ind_val}
                        results = db[entity_name].find(query)
                    elif ind_attr is not None and val is None:
                        db[entity_name].create_index([(ind_attr, ASCENDING)])
                        results = db[entity_name].find({ind_attr: {"$exists": True}})
                    print(results)

    collection_data = {}
    file_name = "mongodb_data.txt"
    with open(file_name, "w") as file:
        pass
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        documents = collection.find()

        with open(file_name, "a") as text_file:
            for doc in documents:
                text_file.write(collection_name + ":\n\n")
                for field in doc:
                    text_file.write(str(field) + ":" + str(doc[field]) + "\n")
                text_file.write("\n\n")

    return send_file("mongodb_data.txt", as_attachment=True)

    
@app.route('/indexing', methods=['POST'])
def indexing():
    coll = request.form.get('text-input-1')
    attr = request.form.get('text-input-2')
    val = request.form.get('text-input-3')
    is_integer = request.form.get('is-integer')  # Get the value of the checkbox

    if is_integer == 'true':
        val = int(val) # Convert val to a string if "is integer" is checked
    else:
        val = val

    # Create an index on the attribute
    db[coll].create_index([(attr, ASCENDING)])
    query = {attr: val}

    # Use the find method with the query
    results = db[coll].find(query)
    print(results)

    return render_template('query_results.html', collection=coll, results=results)

if __name__ == '__main__':
    app.run(debug=True)