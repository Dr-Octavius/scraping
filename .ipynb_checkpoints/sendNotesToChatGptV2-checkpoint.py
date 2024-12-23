import openai
import json
import time
import csv
import ast
from openai.error import ServiceUnavailableError, APIError, Timeout

# Initialize OpenAI API
openai.api_key = "THIS_IS_THE_OPENAI_API_KEY"

hit_rate = 0
miss_rate = 0
service_ok = True

def set_context():
    openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Format for the next prompt:"},
            {"role": "system", "content": "Question Context: Data in the form of a json dictionary that contain interview notes with deal-lost companies"},
            {"role": "system", "content": "Example/Options: Either an example of how to reply, or a basket of options to choose as your reply"},
        ]
    )

def convert_to_json(rtf_text):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": rtf_text},
                {"role": "user", "content": "Restructure all the rtf text above into a json dictionary."},
            ]
        )
        data_str = completion['choices'][0]["message"]['content'] 
        try:
            global hit_rate
            hit_rate += 1
            data = json.loads(data_str)
            return data
        except json.JSONDecodeError:
            global miss_rate
            miss_rate += 1
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "You have provided more than a json dictionary. Please try again. Return only a json dictionary."}
                ]
            )
            return convert_to_json(rtf_text)
    except ServiceUnavailableError:
        raise ServiceUnavailableError
    

def breakdown_json_for_human(json_dict):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": json.dumps(json_dict,indent=2)},
                {"role": "user", "content": "Extract the information above for a human.\n"},
                {"role": "user", "content": "Your human does not read code. Clean any rtf elements from the information.\n"},
                {"role": "user", "content": "Do not be polite.\n"},
                {"role": "user", "content": "Do not be nice.\n"},
                {"role": "user", "content": "Do not summarise.\n"},
                {"role": "user", "content": "Keep the reply short and simple."}
            ]
        )
        completion['choices'][0]["message"]['content'] 
        return completion['choices'][0]["message"]['content']
    except ServiceUnavailableError:
        raise ServiceUnavailableError

def infer_and_update(data, target_dict, key_to_infer, prompt, example):
    try:
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "you are a helpful assistant"},
            ]
        )
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Question Context: " + data},
                {"role": "user", "content": prompt},
                {"role": "user", "content": example},
                {"role": "user", "content": "\nAnswer only as a python list.\n"},
            ]
        )
    except ServiceUnavailableError:
        time.sleep(3)
        raise ServiceUnavailableError
    try:
        global hit_rate
        hit_rate += 1
        reply = ast.literal_eval(completion['choices'][0]["message"]['content'])
        for item in reply:
            if item in target_dict[key_to_infer]:
                continue
            target_dict[key_to_infer].append(item)
        return target_dict
    except:
        global miss_rate
        miss_rate += 1
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Answer only python list."}
            ]
        )
        return infer_and_update(data, target_dict, key_to_infer, prompt, example)

def infer_employee_size_range(data, target_dict):
    prompt = "Question: From the data in the Question Context, what is the employee size of the company? Select one of the options below\n"
    example = "Options: 'Not Mentioned', '1-25', '26-50', '51-100', '101-150', '151-250' or '>251'"
    return infer_and_update(data, target_dict, "Employee Size Range", prompt, example)

def infer_good_to_have_features(data, target_dict):
    prompt = "Question: From the data in the Question Context, what are the good-to-have feature(s) for our software? Below are some features. Select options that answer the question.\n"
    example = "Options: 'Scheduling', 'Time & Attendance', 'Timesheet Consolidation', 'Reports', 'Payroll', 'Leave', 'Casual Labor Management', 'Employee Engagement', 'Others', 'Not Mentioned'"
    return infer_and_update(data, target_dict, "Good to have feature category", prompt, example)

def infer_new_good_to_have_features(data, target_dict):
    prompt = "Question: From the data in the Question Context, what are the suggested good-to-have feature(s) for our software? What are they? Keep responses short. If no mention, reply 'Not Mentioned'\n"
    example = "Example: Given data from the Question Context such as, {'text':'I wish there was a way to log deliveries'}, you would reply with ['Delivery logger']"
    return infer_and_update(data, target_dict, "Good to have feature", prompt, example)

def infer_must_have_features(data, target_dict):
    prompt = "Question: From the data in the Question Context, what are the must-have feature(s) for our software? Below are some features. Select options that answer the question.\n"
    example = "Options: 'Scheduling', 'Time & Attendance', 'Timesheet Consolidation', 'Reports', 'Payroll', 'Leave', 'Casual Labor Management', 'Employee Engagement', 'Others', 'Not Mentioned'"
    return infer_and_update(data, target_dict, "Must have feature category", prompt, example)

def infer_new_must_have_features(data, target_dict):
    prompt = "Question: From the Question Context, are there any suggested must-have features for our software? What are they? Keep responses short. If no mention reply 'Not Mentioned'\n"
    example = "Example: Given data from the Question Context such as, {'text':'I wish there was a way to log deliveries'}, you would reply with ['Delivery logger']"
    return infer_and_update(data, target_dict, "Must have feature", prompt, example)

def infer_closed_lost_reasons(data, target_dict):
    prompt = "Question: From the data in the Question Context, what are the deal lost reasons/deal blockers? Keep responses short. \n"
    example = "Options: Infer a reason or 'Cannot Infer'"
    return infer_and_update(data, target_dict, "Closed lost reasons", prompt,example)

# Test data
initial_dict = {
    "Good to have feature category": [],
    "Good to have feature": [],
    "Must have feature category": [],
    "Must have feature": [],
    "Closed lost reasons": [],
    "Employee Size Range": []
}

# skip 177,277,378 first
index = 932
all_notes = []
big_notes_indexes = []

# Open the file
with open('output.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    # Read each line
    skip_lines = 0
    for row in reader:
        if skip_lines < index:
            skip_lines += 1
            continue
        all_notes.append(row)

# with open('output.txt', 'r') as file:
#     # Read each line
#     skip_lines = 0
#     for line in file:
#         if skip_lines < index:
#             skip_lines += 1
#             continue
#         # Remove leading/trailing whitespaces
#         line = line.strip()
#         if line:
#             # Split the line by commas
#             values = line.split(',')
#             all_notes.append(values)
#         else:
#             all_notes.append([])  # Insert an empty array for empty lines

while service_ok:
    with open("final_data_set2.csv", "a") as file:
        writer = csv.writer(file)
        for notes in all_notes:
            print("writing " + str(index) + " now:")
            print(str(len(notes)) + " notes to process...")
            if len(notes) == 0:
                # Step 0: Write empty line to notes for empty notes
                writer.writerow([[],[],[],[],[],[],[]])
                print(f'written empty: {index}')
                # Start from this index + 1 on next run if OpenAI has issue
                index += 1
                continue

            info_dict = {
                "Good to have feature category": [],
                "Good to have feature": [],
                "Must have feature category": [],
                "Must have feature": [],
                "Closed lost reasons": [],
                "Employee Size Range": []
            }
            to_write=[]
            all_notes=''
            for rtf_note in notes:
                parsed = False
                # gateway to know whether to remove output on data.txt
                while not parsed:
                    try:
                        # Step 0: convert the rtf notes into json
                        data = convert_to_json(rtf_note)
                        all_notes = all_notes + breakdown_json_for_human(data) + "\n"

                        # Step 1: Context setting
                        set_context()
                        
                        data_str = json.dumps(data)
                        # Step 2: Infer employee range
                        next = infer_employee_size_range(data_str,info_dict)
                        
                        # Step 3: Infer good to have features
                        next = infer_good_to_have_features(data_str,next)

                        # Step 3: Infer new good to have features
                        next = infer_new_good_to_have_features(data_str,next)

                        # Step 4: Infer must have features
                        next = infer_must_have_features(data_str,next)

                        # Step 4: Infer new must have features
                        next = infer_new_must_have_features(data_str,next)

                        # Step 5: Infer closed lost reasons
                        info_dict = infer_closed_lost_reasons(data_str,next)
                    except ServiceUnavailableError:
                        service_ok = False
                        break
                    except APIError:
                        time.sleep(5)
                        continue
                    except Timeout:
                        time.sleep(5)
                        continue
                    else:
                        parsed = True
                        continue
            
            # Step 6: Write the collated notes to the array
            to_write.append(all_notes)

            # Step 7: Clean dictionary for our context
            for key, value in info_dict.items():
                result = ""
                added_Not_Mentioned = False
                added_Cannot_Infer = False
                for item in value:
                    if item == "Not Mentioned":
                        if not added_Not_Mentioned:
                            added_Not_Mentioned = True
                        continue
                    if item == "Cannot Infer":
                        if not added_Cannot_Infer:
                            result += "Refer to Notes"
                            added_Cannot_Infer = True
                        continue
                    result = result + str(item) + ","
                to_write.append(str(result))
            
            # Step 8: Write to file
            writer.writerow(to_write)
            print(f'written: {index}')

            # Start from this index + 1 on next run if OpenAI has issue
            index += 1

print("Total hits: " + str(hit_rate))
print("Total misses: " + str(miss_rate))
print("Accuracy: " + str(hit_rate/(hit_rate+miss_rate)))
print("Total records parsed: " + str(index))
print("These notes are huge: " + str(big_notes_indexes))