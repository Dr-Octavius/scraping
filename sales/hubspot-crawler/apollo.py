import requests

url = "https://api.apollo.io/v1/emailer_campaigns/search"

data = {
    "api_key": "",
    "q_name": "Michael's Drip"
}

headers = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, json=data)

print(response.text)