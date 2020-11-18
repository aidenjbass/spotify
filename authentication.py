import base64
import datetime
import requests

client_id = '06f1f688ba144e21b3594f8dddc4a35c'  # given by spotify api dashboard, kept constant for use case
client_secret = 'bd81aa1b4e814cc7915c03839af073bd'  # given by spotify api dashboard, can be revoked at anytime

client_credentials = f'{client_id}:{client_secret}'
client_credentials_base64 = base64.b64encode(client_credentials.encode())  # as seen below, base64 is required

print(client_credentials_base64)

access_token_url = 'https://accounts.spotify.com/api/token'  # this is the endpoint given by the spotify API

# access_method = 'POST'

token_data = {
    'grant_type': 'client_credentials'
}

token_header = {
    'Authorization': f'Basic {client_credentials_base64.decode()}'
    # 'Basic <base64 encoded client_id:client_secret>' format given by spotify API
}

print(token_header)

r1 = requests.post(access_token_url, data=token_data, headers=token_header)

print(r1.json())

valid_request = r1.status_code in range(200, 299)

print(valid_request)

token_response_data = r1.json()
now = datetime.datetime.now()
expires_in = token_response_data['expires_in']  # in seconds
expires_at = now + datetime.timedelta(seconds=expires_in)

print(expires_at)

# token = token_response_data['access_token']
# print(token)
