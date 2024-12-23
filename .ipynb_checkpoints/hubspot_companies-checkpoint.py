from enum import Enum
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from collections import deque
import requests
import datetime

# log API Call limit
limit = -9999999

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
    GET_DEALS = 4

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

def convert_to_timestamp_str(year : int, month : int, day : int, hour : int, minute : int, second : int):
    # Example datetime object
    dt = datetime.datetime(year, month, day, hour, minute, second)
    # Convert datetime to timestamp in milliseconds
    timestamp_ms = int(dt.timestamp() * 1000)
    # Convert timestamp to string
    timestamp_str = str(timestamp_ms)
    return timestamp_str
     
# Implement AND logic by having multiple params within filters i.e. new_filter["filter"].append(dict) == AND
def time_filter_companies(time1 : str, time2 : str):
    result = new_filter()
    result["filters"].append({
        "propertyName":"createdate",
        "operator":"BETWEEN",
        "highValue": time1,
        "value":time2
    })
    return result

def search_for_companies():
    # Basic info
    target_url = select_url(Operations.COMPANY_SEARCH)
    target_headers = request_header()
    # Add your data here
    target_filters = filters()
    target_filters["filterGroups"].append(time_filter_companies(
        convert_to_timestamp_str(2022, 1, 31, 11, 59, 59),
        convert_to_timestamp_str(2022, 1, 1, 0, 0, 0),  # Earliest record is December 17th 2017
    ))
    data = {**target_filters, **max_limit(), **default_property()}

    # Execute initial request to get total results
    initial_response = execute_query(RequestTypes.POST)(url=target_url, headers=target_headers, json=data)
    total_results = initial_response.json()["total"]
    # Determine the number of requests needed
    num_requests = total_results // 100
    if (num_requests == 0):
        return initial_response.json()["results"]
    
    # print(initial_response.json()["results"])
    # Perform paginated requests to retrieve all results
    all_results = []
    all_results.extend(initial_response.json()["results"])
    data = {**data,**paging()}
    while (num_requests > 0):
        response = execute_query(RequestTypes.POST)(url=target_url, headers=target_headers, json=data)
        results = response.json()["results"]
        all_results.extend(results)
        data["after"] += 100
        num_requests -= 1
    return all_results


def get_company_to_notes_association(id : str):
    # add your GET request info here
    target_params = params()
    target_params["associations"] = "notes"
    # basic info
    target_url = f"{select_url(Operations.GET_COMPANIES)}/{id}?{urlencode(target_params)}"
    target_headers = request_header()

    return execute_query(RequestTypes.GET)(url=target_url,headers=target_headers)

# GET notes object based on ID
def get_notes_from_id(id : str):
    # add your GET request info here
    target_params = params()
    target_params["properties"] += "hs_note_body"
    # basic info
    target_url = f"{select_url(Operations.GET_NOTES)}/{id}?{urlencode(target_params)}"
    target_headers = request_header()
    
    return execute_query(RequestTypes.GET)(url=target_url,headers=target_headers)

# GET deals object based on ID
def get_deals_from_id(id : str):
    # add your GET request info here
    target_params = params()
    target_params["properties"] += "hs_note_body"
    target_params["associations"] = "company"
    # basic info
    target_url = f"{select_url(Operations.GET_DEALS)}/{id}?{urlencode(target_params)}"
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

# This function is created becuase associations only resturns the id
# Additional operations are required to get the content of the object based on this id
# 
# Key assumptions: you must know what you are searching for 
# 
# As a plus, this logic also handles pagination (and how it should be done in python)
def search_for_note_body(search_data : dict):
    
    # Create a master list to return as a result
    master_list = []

    for search in search_data:
        
        # Store new entries in a data structure of your choice
        
        new_entry = []
        
        # Each piece of data in seacrh can be accessede via a key
        # You can access as many key-value pairs as you want as long as you know the key
        # new_entry.append([search["some_key_1"],search["some_key_2"]])
        
        # Retrieve associated data by calling the api using pre-built functions 
        # above
        # 
        # "id" is a safe key since all objects have it
        # 
        # We will use the below function as a worked example

        response = get_company_to_notes_association(search["id"])
        unpacked_data = response.json()
        

        # log limit (in the case that we one day care about limits)
        # limit = int(response.headers["X-HubSpot-RateLimit-Daily-Remaining"])
        # if int(response.headers["X-HubSpot-RateLimit-Remaining"]) <= 120:
        #     time.sleep(2)

        # Conditionals to choose which prop/association you are searching for
        # Refer to POST possible data comment to get an idea
        # 
        # Boilerplate example below (finding notes based on associations):
        # 
        # In the happy path, the data has no notes associated with it 
        # Based on the data structure you have decided on above you can  
        if "associations" not in unpacked_data:
            
            # Flexible to use any placeholder value for empty searches
            new_entry.append(["NO NOTES"])
        else:
            
            all_notes = unpacked_data["associations"]["notes"]["results"]
            notes_data = []
            for note in all_notes:
                note_response = get_notes_from_id(note["id"])
                note_data = note_response.json()
                if note_data["properties"]["hs_note_body"] == None:
                    continue
                # log limit (in the case that we one day care about limits)
                # limit = int(note_response.headers["X-HubSpot-RateLimit-Daily-Remaining"])
                # find current limit
                # if int(note_response.headers["X-HubSpot-RateLimit-Remaining"]) <= 135:
                #     time.sleep(1)
                notes_data.append([note_data["id"],note_data["properties"]["hs_note_body"]])
                
                # We can use beutiful to soup to store any html-based object into a tree
                soup = BeautifulSoup(note_data["properties"]["hs_note_body"], 'html.parser')

                # traverse function will go through the tree
                final = traverse(soup)
                    
            new_entry.append(notes_data)
        master_list.append(new_entry)
    return master_list

# Run your queries here
company_search_data = search_for_companies()
# For Debugging Response:
# print(json.dumps(company_search_data, indent=2))
# logging line
print("\n",len(company_search_data),"results\n")
# post request come in as json (search query not counted as call)

# log limit (in the case that we one day care about limits)
# print("\nCalls Left: ", limit)

# # Specify the CSV file path
# csv_file = '../hubspot_lostDeals.csv'

# # Read the CSV file into a DataFrame, skipping the first header row
# df = pd.read_csv(csv_file, skiprows=1) 

# # Rename the columns based on the second header row
# new_columns = df.columns.str.replace('Unnamed: 0', 'Company Name')
# df.columns = pd.MultiIndex.from_arrays([new_columns, df.iloc[0]])
# df = df.iloc[1:]

# # Reset the column names and remove any remaining duplicate header row
# df.columns = df.columns.get_level_values(1)
# df = df.reset_index(drop=True)

# # Print the DataFrame
# print(df)