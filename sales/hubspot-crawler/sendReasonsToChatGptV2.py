import openai
import json
import time
import csv
import ast
from openai.error import ServiceUnavailableError, APIError, Timeout

# Initialize OpenAI API
# set this
openai.api_key = ""
categories = ['Price/Budget','Bad Follow Up','Ghosted','Not Decision Maker','Bad Fit / Unqualified','Not Urgent','Using Competitor','Lack of Feature','Others']

hit_rate = 0
miss_rate = 0
service_ok = True

def set_context():
    openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Format for the next prompt:"},
            {"role": "system", "content": "\nQuestion Context: Data will be provided as single strings or comma separated strings. The data are reasons for customers churning."},
            {"role": "system", "content": "\nOptions: A list of categories to choose as your reply"},
        ]
    )

def infer_and_update(data, target_dict, key_to_infer, prompt, example):
    print("inferring...")
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
                {"role": "user", "content": "\nAnswer only 1 category. Keep responses short\n"},
            ]
        )
    except ServiceUnavailableError:
        time.sleep(3)
        raise ServiceUnavailableError
    try:
        global hit_rate
        hit_rate += 1
        reply = completion['choices'][0]["message"]['content']
        if reply not in categories:
            raise Exception
        else:
            if reply not in target_dict[key_to_infer]:
                target_dict[key_to_infer].append(completion['choices'][0]["message"]['content'])
            return target_dict
    except:
        global miss_rate
        miss_rate += 1
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Answer only 1 category from " + ' '.join(categories) + " .Keep responses short."}
            ]
        )
        return infer_and_update(data, target_dict, key_to_infer, prompt, example)

def infer_deal_lost_category(data, target_dict):
    prompt = "\nQuestion: From the Question Context, choose 1 category below that most accurately matches the Question Context. 'Payroll' is a feature. 'Freemium' is a free version."
    example = "\nOptions: 'Price/Budget','Bad Follow Up','Ghosted','Not Decision Maker','Bad Fit / Unqualified','Not Urgent','Using Competitor','Lack of Feature','Others'"
    return infer_and_update(data, target_dict, "Deal Lost Category", prompt,example)

# Test data
initial_dict = {
    "Deal Lost Category": [],
}

index = 0
all_deal_lost_reasons = []
big_notes_indexes = []

# Open the file
with open('deal_lost_reasons.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    # Read each line
    skip_lines = 0
    for row in reader:
        if skip_lines < index:
            skip_lines += 1
            continue
        all_deal_lost_reasons.append(row)

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
    if (index == len(all_deal_lost_reasons)):
        break
    with open("output.csv", "a") as file:
        writer = csv.writer(file)
        for deal_lost_reasons in all_deal_lost_reasons:
            
            print("writing " + str(index) + " now:")
            if len(deal_lost_reasons) == 0:
                # Step 0: Write empty line to notes for empty notes
                writer.writerow([[]])
                print(f'written empty: {index}')
                # Start from this index + 1 on next run if OpenAI has issue
                index += 1
                continue
            
            if (len(deal_lost_reasons)==1):
                seperated_deal_lost_reasons = deal_lost_reasons[0].split(',')
                print(str(len(seperated_deal_lost_reasons)) + " deal lost reason(s) to process...")
            else:
                seperated_deal_lost_reasons = deal_lost_reasons
                print(str(len(seperated_deal_lost_reasons)) + " deal lost reason(s) to process...")
            info_dict = {
                "Deal Lost Category": []
            }
            to_write=[]
            for deal_lost_reason in seperated_deal_lost_reasons:
                parsed = False
                # gateway to know whether to remove output on data.txt
                while not parsed:
                    print("parsing reason: " + deal_lost_reason)
                    try:

                        # Step 1: Context setting
                        set_context()
                        
                        # Step 2: Infer deal lost category
                        initial_dict = infer_deal_lost_category(deal_lost_reason,info_dict)
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
            
            # Step 6: Write the collated deal lost reasons to the array
            to_write.append(deal_lost_reasons)

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
                            result += "Refer to Left Column"
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