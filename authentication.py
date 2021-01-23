import base64
import datetime
import requests

client_id = '06f1f688ba144e21b3594f8dddc4a35c'  # given by spotify api dashboard, kept constant for use case
client_secret = 'bd81aa1b4e814cc7915c03839af073bd'  # given by spotify api dashboard, can be revoked at anytime

client_credentials = f'{client_id}:{client_secret}'  # f string to form correct input
client_credentials_base64 = base64.b64encode(client_credentials.encode())  # as seen below, base64 is required
# python base64 module is used to encode data, .encode() is to encode in Unicode which is needed by base64 module

print(client_credentials_base64)  # printing variables throughout program to check for errors

access_token_url = 'https://accounts.spotify.com/api/token'  # this is the endpoint given by API

# access_method = 'POST' given by API

token_data = {  # dictionary data type that can be used in URL creation
    'grant_type': 'client_credentials'
}

token_header = {  # dictionary data type that can be used in URL creation
    'Authorization': f'Basic {client_credentials_base64.decode()}'
    # 'Basic <base64 encoded client_id:client_secret>' format given by  API
}

print(token_header)  # printing variables throughout program to check for errors

r1 = requests.post(access_token_url, data=token_data, headers=token_header)
# uses python requests module to make a HTTP request to the spotify API

print(r1.json())    # printing variables throughout program to check for errors

valid_request = r1.status_code in range(200, 299)  # simple check to to see if request was accepted by API, 2xx is valid

print(valid_request)  # printing variables throughout program to check for errors

token_response_data = r1.json()
now = datetime.datetime.now()
expires_in = token_response_data['expires_in']  # in seconds
expires_at = now + datetime.timedelta(seconds=expires_in)

print(expires_at)  # printing variable throughout program to check for errors

token = token_response_data['access_token']
print(token)  # printing variable throughout program to check for errors
