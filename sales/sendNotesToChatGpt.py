import openai
import json
openai.api_key = ""

all_notes = []

# Open the file
with open('output.txt', 'r') as file:
    # Read each line
    for line in file:
        # Remove leading/trailing whitespaces
        line = line.strip()
        if line:
            # Split the line by commas
            values = line.split(',')
            all_notes.append(values)
        else:
            all_notes.append([])  # Insert an empty array for empty lines

index = 0

final = {
    "Good to have feature category": [],
    "Good to have feature": [],
    "Must have feature category": [],
    "Must have feature": [],
    "Closed lost reasons": [],
    "Employee Size": ""
}

for notes in all_notes:
    for note in notes:
        while True:
            try:
                completion1 = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": note},
                        {"role": "user", "content": "Please convert the above rtf into a json dictionary using only the text content"}
                    ]
                )
                raw_output = completion1['choices'][0]["message"]['content']
                raw_dict = json.loads(raw_output)
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "The solution is correct!\n" + raw_output},
                    ]
                )
                print(json.dumps(raw_dict,indent=2))
                break
            except json.JSONDecodeError as e:
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "Only return the json dictionary!\n" + raw_output},
                    ]
                )
        while True:
            completion2 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Use the below dictionary as a data set\n" + raw_output},
                    {"role": "user", "content": "Fill the values of the below json dictionary from the data set.\n" + json.dumps(final)},
                    {"role": "user", "content": "\nReturn only a json dictionary."}
                ]
            )
            inferred_cleaning = completion2['choices'][0]["message"]['content']
            try:
                inferred_cleaning_dict = json.loads(inferred_cleaning)
                final = inferred_cleaning_dict
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "The solution is correct!\n" + raw_output},
                    ]
                )
                print(json.dumps(inferred_cleaning_dict,indent=2))
                break
            except json.JSONDecodeError as e:
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "The solution is wrong! Only return a json dictionary!\n" + raw_output},
                    ]
                )
        while True:
            completion3 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Use the below dictionary as a data set\n" + raw_output},
                    {"role": "user", "content": "Place anything from the data set that sounds like a reson for losing business in the dictionary below in the 'closed lost reason' key\n" + json.dumps(final)},
                    {"role": "user", "content": "\nReturn only a json dictionary."}
                ]
            )
            final_cleaning = completion3['choices'][0]["message"]['content']
            try:
                final = json.loads(final_cleaning)
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "The solution is correct!\n" + raw_output},
                    ]
                )
                print(json.dumps(final,indent=2))
                break
            except json.JSONDecodeError as e:
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "The solution is wrong! Only return a json dictionary!\n" + raw_output},
                    ]
                )
        index += 1