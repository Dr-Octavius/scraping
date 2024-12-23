from enum import Enum
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import csv

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
    return 'THIS_IS_THE_HUBSPOT_OAUTH_KEY'

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
                dom_dictionary[soup.name].append(soup.string)
            else:
                dom_dictionary[soup.name].append(traverse(child))
        return dom_dictionary

# Specify the CSV file path
csv_file = '../hubspot_closedDeals2022.csv'

# Read the CSV file into a DataFrame, skipping the first header row
df = pd.read_csv(csv_file) 

# Add a new notes column with a single value
df['Notes'] = [[]] * len(df)
limit = -99999

# Iterate through the "Record ID" column by directly accessing the Series
for index, row in df.iterrows():
    if index < 498:
        continue
    deal_response = get_deal_to_notes_association(row['Record ID'])
    deal_response_data =  deal_response.json()
    if "associations" not in deal_response_data:
        continue
    all_notes = deal_response_data["associations"]["notes"]["results"]
    notes_data = []
    for note in all_notes:
        note_response = get_notes_from_id(note["id"])
        note_data = note_response.json()
        if note_data["properties"]["hs_note_body"] == None:
            continue
        notes_data.append(note_data["properties"]["hs_note_body"])
    df.at[index, 'Notes'] = notes_data
    print(index)

print(limit)
# Convert nested arrays to string representations
# df['Notes'] = df['Notes'].apply(lambda x: ', '.join(x) if len(x) > 0 else '')

# Replace NaN values in the empty arrays with empty strings
# df['Notes'] = df['Notes'].replace(np.nan, '')

# Open a text file for writing
with open('output.csv', 'w') as file:
    writer = csv.writer(file)
    # Iterate over the 'html_column' values
    for arr in df['Notes']:
        writer.writerow(arr)  # Add a newline after each HTML text

# # Rename the columns based on the second header row
# new_columns = df.columns.str.replace('Unnamed: 0', 'Company Name')
# df.columns = pd.MultiIndex.from_arrays([new_columns, df.iloc[0]])
# df = df.iloc[1:]

# # Reset the column names and remove any remaining duplicate header row
# df.columns = df.columns.get_level_values(1)
# df = df.reset_index(drop=True)