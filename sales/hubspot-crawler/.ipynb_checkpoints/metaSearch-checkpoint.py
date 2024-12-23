import requests

# Replace {access-token} with your actual access token
client_id = '6880145348731431'
client_secret = 'f5e015138af2e52bc346bb1a7c412103'
access_token = ''

# The API URL and query parameters
login_url = 'https://graph.facebook.com/oauth/access_token'
params = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'client_credentials'
}

# Make the GET request
response = requests.get(login_url, params=params)

# If you want to handle the response in JSON format
if response.ok:
    access_token = response.json()['access_token']
    search_url = 'https://graph.facebook.com/pages/search'
    params = {
        'q': 'Facebook',
        'fields': 'id,name,location,link',
        'access_token': access_token
    }
    response = requests.get(search_url, params=params)
    # Print out the response content or headers depending on the need
    print(response.headers)
    print(response.text)
else:
    print('Error:', response.status_code)
