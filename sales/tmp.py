from enum import Enum
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import pandas as pd
import requests
import lxml

class RequestTypes(Enum):
    GET = 1
    POST = 2
    PATCH = 3
    DELETE = 4

class Operations(Enum):
    COMPANY_SEARCH = 1
    NOTES_SEARCH = 2
    GET_NOTES = 3
    GET_COMPANIES = 4
    GET_DEALS = 5

# POST Possible Data
# Implement OR logic by having mutlple filters i.e. filters.append(new_filter()) == OR
def filters():
    return { "filterGroups" : [] }
def new_filter():
    return { "filters" : [] }
def sort():
    return { "sorts" : [] }
def contains_custom():
    return { "query" : "" }
def max_limit():
    return { "limit" : 100 }
def default_property():
    return { "properties" : [] }
def default_associations():
    return { "associations" : [] }
def paging():
    return { "after" : 100 }

# GET Params
def params():
    return {
        'limit': '100',
        'properties': '',
        'associations': '',
        'archived': 'true',
    }

def get_token():
    return ''

def request_header():
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token()}'
    }

def select_url(op : Operations):
    if op == Operations.COMPANY_SEARCH:
        return 'https://api.hubapi.com/crm/v3/objects/companies/search'
    elif op == Operations.NOTES_SEARCH:
        return 'https://api.hubapi.com/crm/v3/objects/notes/search'
    elif op == Operations.GET_NOTES:
        return 'https://api.hubapi.com/crm/v4/objects/notes'
    elif op == Operations.GET_COMPANIES:
        return 'https://api.hubapi.com/crm/v4/objects/companies'
    elif op == Operations.GET_DEALS:
        return 'https://api.hubapi.com/crm/v4/objects/deals'
    else:
        raise ValueError('Invalid API constant specified.')

def execute_query(requestType : RequestTypes):
    if requestType == RequestTypes.GET:
        return requests.get
    elif requestType == RequestTypes.POST:
        return requests.post
    elif requestType == RequestTypes.PATCH:
        return requests.patch
    elif requestType == RequestTypes.DELETE:
        return requests.delete

def get_deal_to_notes_association(id : str):
    # add your GET request info here
    target_params = params()
    target_params["associations"] += "notes"
    # basic info
    target_url = f"{select_url(Operations.GET_DEALS)}/{id}?{urlencode(target_params)}"
    target_headers = request_header()

    return execute_query(RequestTypes.GET)(url=target_url,headers=target_headers)

def get_notes_from_id(id : str):
    # add your GET request info here
    target_params = params()
    target_params["properties"] += "hs_note_body"
    filtered_params = {k: v for k, v in target_params.items() if v}
    # basic info
    target_url = f"{select_url(Operations.GET_NOTES)}/{id}?{urlencode(filtered_params)}"
    target_headers = request_header()
    return execute_query(RequestTypes.GET)(url=target_url,headers=target_headers)

def traverse(soup):
    if soup.name is not None:
        dom_dictionary = {}
        dom_dictionary[soup.name] = []
        for child in soup.children:
            print(child)
            if child is None:
                continue
            elif isinstance(child,str):
                print(isinstance(child,str))
                dom_dictionary[soup.name].append(soup.string)
            else:
                dom_dictionary[soup.name].append(traverse(child))
        return dom_dictionary

def extract_info_A(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = {}
    step = 0
    step_key = ''

    for p_tag in soup.find_all(['p']):
        text = p_tag.get_text()
        strong_text = p_tag.find('strong')
        if text == "":
            continue
        print(text)
        if text == "--- DEAL INFORMATION ---" or text == "--- SPICD ---":
            step = 0
            continue
        if text == "What do they love about us" or text == "Deal blocker(s) ":
            step = 1
            step_key = text
            result[step_key] = []
            continue
        if step == 1:
            result[step_key].append(text)
            continue
        if text == "--- FURTHER NEEDS ---":
            step = 2
            continue
        if step == 2 and (strong_text.get_text().find("Category") != -1 or strong_text.get_text().find("Feature") != -1):
            category_or_feature, *value = text.split(":", 1)
            if len(value) > 0 :
                result[step_key][category_or_feature.strip()].append(value[0])
            continue
        elif step == 2 and strong_text:
            step_key = text
            result[step_key] = {"Category" : [], "Feature" : []}
            continue
        key, value = text.split(":", 1)
        key = key.strip()
        value = value.strip()
        result[key] = value
    return result

def extract_info_C(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = {}
    step = 0
    step_key = ''

    for p_tag in soup.find_all():
        text = p_tag.get_text()
        strong_text = p_tag.find('strong')
        if text == "":
            continue
        print(text)
        # if text == "--- DEAL INFORMATION ---" or text == "--- SPICD ---":
        #     step = 0
        #     continue
        # if text == "What do they love about us" or text == "Deal blocker(s) ":
        #     step = 1
        #     step_key = text
        #     result[step_key] = []
        #     continue
        # if step == 1:
        #     result[step_key].append(text)
        #     continue
        # if text == "--- FURTHER NEEDS ---":
        #     step = 2
        #     continue
        # if step == 2 and (strong_text.get_text().find("Category") != -1 or strong_text.get_text().find("Feature") != -1):
        #     category_or_feature, *value = text.split(":", 1)
        #     if len(value) > 0 :
        #         result[step_key][category_or_feature.strip()].append(value[0])
        #     continue
        # elif step == 2 and strong_text:
        #     step_key = text
        #     result[step_key] = {"Category" : [], "Feature" : []}
        #     continue
        # key, value = text.split(":", 1)
        # key = key.strip()
        # value = value.strip()
        # result[key] = value
    return result

def extract_dictionaries(html):
    soup = BeautifulSoup(html, 'html.parser')
    dictionaries = {'A':[],'B':[],'C':[]}
    current_dict = {}
    for tag in soup.find_all(['strong', 'p']):
        if tag.name == 'strong':
            strong_text = tag.get_text(strip=True)
            if strong_text.startswith('Deal Name'):
                current_dict = extract_info_A(html)
                dictionaries['A'].append(current_dict)
                break
            elif strong_text == '--- BASIC INFO ---':
                print("B this")
                current_dict = {}
                current_dict[strong_text] = ''
                dictionaries.append(current_dict)
            elif strong_text == 'Lead Information':
                print("C this")
                current_dict = extract_info_C(html)
                current_dict[strong_text] = ''
                dictionaries.append(current_dict)
        elif tag.name == 'p' and current_dict:
            strong_tag = tag.find('strong')
            if strong_tag:
                key = strong_tag.get_text(strip=True)
                value = tag.get_text(strip=True).replace(key, '').strip()
                current_dict[key] = value
    return dictionaries


# Specify the CSV file path
csv_file = '../hubspot_lostDeals.csv'

# Read the CSV file into a DataFrame, skipping the first header row
df = pd.read_csv(csv_file) 

# Add a new notes column with a single value
df['Notes'] = 'NO NOTES'
note_id = '29123656704'

# Iterate through the "Record ID" column by directly accessing the Series
note_response = get_notes_from_id(note_id)
note_data = note_resnote_response = get_notes_from_id(note_id)
note_data = note_response.json()

# We can use beutiful to soup to store any html-based object into a tree
# final = extract_dictionaries(note_data["properties"]["hs_note_body"])
print(note_data["properties"]["hs_note_body"])

# # Rename the columns based on the second header row
# new_columns = df.columns.str.replace('Unnamed: 0', 'Company Name')
# df.columns = pd.MultiIndex.from_arrays([new_columns, df.iloc[0]])
# df = df.iloc[1:]

# # Reset the column names and remove any remaining duplicate header row
# df.columns = df.columns.get_level_values(1)
# df = df.reset_index(drop=True)

