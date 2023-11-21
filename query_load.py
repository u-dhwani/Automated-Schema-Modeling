import pandas as pd
import csv

# Specify the path to your text file
csv_file_path = "input_files/my_stack_overflow_relation.csv"
txt_file_path = "input_files/mso_query.txt"

df = pd.read_csv(csv_file_path)
data = df.to_dict(orient="records")

# Initialize a list to store the split values for each line
split_lines = []
lists_dict = {}
entity_attributes = {}

with open(csv_file_path, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)  # Skip the header row

    for row in csv_reader:
        entity1, entity2, rel, card1, card2 = row

# Open the text file in read mode
with open(txt_file_path, 'r') as file:
    # Read each line in the file
    for i, line in enumerate(file, start=1):
        # Split the line by '/' and store the split values in a list
        values = line.strip().split('/')
        # Append the list of split values to the result list
        split_lines.append(values)

        list_name = f"list_{i}"
        lists_dict[list_name] = values
        # print(lists_dict[list_name])
        # print(lists_dict.items())
        # print("-" * 20)

# Get the number of lines in the file
num_lines = len(lists_dict)

# print("vals:", values)

for list_name, values in lists_dict.items():
    for i in values:
        parts = i.split("?")
        print(parts)
    if len(parts) == 2:
    # Extract the word or words after the question mark
        word_after_question_mark = parts[1].strip()
        print(word_after_question_mark)
    else:
        print("No question mark found in the input string.")
    # print(list_name, values)

    answer = ""
    for i in range(len(values) - 1):
        curr_element = values[i]
        next_element = values[i+1]
        matching_row = df[(df['Entity1'].str.lower() == curr_element) & (df['Entity2'].str.lower() == next_element)]
        rev_match = df[(df['Entity2'].str.lower() == curr_element) & (df['Entity1'].str.lower() == next_element)]

        if not matching_row.empty:
            # If a matching row is found, print the RelationshipName, Card1, and Card2
            relationship_name = matching_row['RelationshipName'].values[0]
            card1 = matching_row['Card1'].values[0]
            card2 = matching_row['Card2'].values[0]

            answer+="("
            if card1 == 1 and card2 > 500: # one-to-many as well as one-to-squillion
                answer+=curr_element+" references "+next_element+")"
            elif card1 == 1 and card2 <= 500: 
                answer+=curr_element+" embeds "+next_element+")"
            elif card1 > 1 and card2 == 1:
                answer+=next_element+" references "+curr_element+")"
            elif card1 > 1 and card2 > 1:
                answer+=curr_element+" references "+next_element+" and "
                answer+=next_element+" references "+curr_element+")"
        
        if not rev_match.empty:
            # If a matching row is found, print the RelationshipName, Card1, and Card2
            relationship_name = rev_match['RelationshipName'].values[0]
            card1 = rev_match['Card1'].values[0]
            card2 = rev_match['Card2'].values[0]

            answer+="("
            if card1 == 1 and card2 > 500: # one-to-many as well as one-to-squillion
                answer+=next_element+" references "+curr_element+")"
            elif card1 == 1 and card2 <= 500: 
                answer+=next_element+" embeds "+curr_element+")"
            elif card1 > 1 and card2 == 1:
                answer+=curr_element+" references "+next_element+")"
            elif card1 > 1 and card2 > 1:
                answer+=curr_element+" references "+next_element+" and "
                answer+=next_element+" references "+curr_element+")"

    if answer == "":
        print("No relationship found")
        print("-" * 20)
    else:
        print(answer)
        print("-" * 20)