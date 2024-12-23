from enum import Enum
from urllib.parse import urlencode
import requests
import concurrent.futures
import time
import json
import datetime
import pandas

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
    return { "limit" : 20 }
def default_property():
    return { "properties" : [] }
def paging():
    return { "paging.next.after" : 20 }

# GET Params
def params():
    return {
        'limit': '100',
        'properties': '',
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
def time_filter_notes(time1 : str, time2 : str):
    result = new_filter()
    result["filters"].append({
        "propertyName":"hs_createdate",
        "operator":"BETWEEN",
        "highValue": time1,
        "value":time2
    })
    return result

def search_for_notes():
    # basic info
    target_url = select_url(Operations.NOTES_SEARCH)
    target_headers = request_header()
    # add your data here
    target_filters = filters()
    target_filters["filterGroups"].append(time_filter_notes(
        convert_to_timestamp_str(2018,12,31,11,59,59),
        convert_to_timestamp_str(2017,12,1,0,0,0), #earliest record is December 17th 2017
    ))
    props = default_property()
    props["properties"].append("hs_note_body")
    data = {**target_filters,**max_limit(),**paging(),**props}
    return execute_query(RequestTypes.POST)(url=target_url,headers=target_headers,json=data)

def get_notes_to_company_association(id : str):
    # add your GET request info here
    target_params = params()
    target_params["associations"] += "company"
    # basic info
    target_url = f"{select_url(Operations.GET_NOTES)}/{id}?{urlencode(target_params)}"
    target_headers = request_header()
    # print(target_url)
    return execute_query(RequestTypes.GET)(url=target_url,headers=target_headers)

def get_company_from_id(id : str):
    # add your GET request info here
    target_params = params()
    # basic info
    target_url = f"{select_url(Operations.GET_COMPANIES)}/{id}?{urlencode(target_params)}"
    target_headers = request_header()
    print(target_url)
    return execute_query(RequestTypes.GET)(url=target_url,headers=target_headers)

# Run your queries here
notes_search_data = search_for_notes().json()
print("\n",notes_search_data["total"],"results\n")
# post request come in as json (search query not counted as call)
# For Debugging Response:
print(json.dumps(notes_search_data, indent=2))

company_notes = []

for notes_data in notes_search_data["results"]:
    new_entry = []
    new_entry.append([notes_data["id"],notes_data["properties"]["hs_note_body"]])
    company_from_notes = get_notes_to_company_association(notes_data["id"])
    company_from_notes_data = company_from_notes.json()
    print(company_from_notes_data)
    # log limit
    limit = int(company_from_notes.headers["X-HubSpot-RateLimit-Daily-Remaining"])
    if int(company_from_notes.headers["X-HubSpot-RateLimit-Remaining"]) <= 120:
        time.sleep(2)
    
    company_data = get_company_from_id(company_from_notes_data["associations"]["companies"]["results"][0]["id"])
    
    new_entry.append([company_data["properties"]["name"],company_data["properties"]["domain"]])
        
    company_notes.append(new_entry)