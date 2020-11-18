import base64
import requests
import datetime
from urllib.parse import urlencode

client_id = '06f1f688ba144e21b3594f8dddc4a35c'
client_secret = 'bd81aa1b4e814cc7915c03839af073bd'

client_credentials = f'{client_id}:{client_secret}'
client_credentials_base64 = base64.b64encode(client_credentials.encode())

# print(client_credentials_base64)

access_token_url = 'https://accounts.spotify.com/api/token'
access_method = 'POST'

token_data = {
    'grant_type': 'client_credentials'
}
token_headers = {
    'Authorization': f'Basic {client_credentials_base64.decode()}'
    # 'Basic <base64 encoded client_id:client_secret>'
}

# print(token_headers)

r1 = requests.post(access_token_url, data=token_data, headers=token_headers)
# print(r1.json())

valid_request = r1.status_code in range(200, 299)
# print(valid_request)

# if valid_request is True:
token_response_data = r1.json()
now = datetime.datetime.now()
token = token_response_data['access_token']
expires_in = token_response_data['expires_in']  # in seconds
expires_at = now + datetime.timedelta(seconds=expires_in)
# print(expires_at)
has_expired = expires_at < now
# print(has_expired)
# print(token)

"""
Start of code to search Spotify API
"""

header = {
    'Authorization': f'Bearer {token}'
}
endpoint = 'https://api.spotify.com/v1/search'
search_query = urlencode({'q': 'betty', "type": "track"})
print(search_query)

lookup_url = f'{endpoint}?{search_query}'
print(lookup_url)
r2 = requests.get(lookup_url, headers=header)
print(r2.status_code)
print(r2.json())