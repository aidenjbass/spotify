import datetime
import base64


class ClientAuth(object):  # this class is just for the Client authentication part of the Spotify API
    # constant setting
    token = None
    token_expires_at = datetime.datetime.now()
    token_has_expired = True
    token_url = "https://accounts.spotify.com/api/token"

    # client_id and and client_secret are now constants stored in the external file secrets.py
    client_id = None
    client_secret = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        # returns the base64 string
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise Exception('client_id or client_secret not set')
        else:  # encodes the credentials in base64 encoding rather than UTF, which is required by the API
            client_credentials = f'{client_id}:{client_secret}'
            client_credentials_base64 = base64.b64encode(client_credentials.encode())
            return client_credentials_base64.decode()

    @staticmethod  # a static method that simply stores the grant_type required by the API
    def get_token_data():
        return {
            'grant_type': 'client_credentials'
        }

    def get_token_header(self):  # combines the authorization type and header data needed by the API
        client_credentials_base64 = self.get_client_credentials()
        return {
            'Authorization': f'Basic {client_credentials_base64}'
        }

    def authenticate(self):
        # calling constants returned from previous functions
        access_token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()
        # calls API to retrieve the client token used throughout the program later on to interact with API
        r1 = requests.post(access_token_url,
                           data=token_data,
                           headers=token_headers)
        valid_request = r1.status_code in range(200, 299)  # anything outside this range is invalid
        if valid_request is False:
            raise Exception('Authetication failed')
        else:
            response_data = r1.json()
            now = datetime.datetime.now()
            token = response_data['access_token']
            expires_in = response_data['expires_in']  # in seconds, will typically give a value of 3600 seconds
            expires_at = now + datetime.timedelta(seconds=expires_in)
            self.token = token
            self.token_expires_at = expires_at
            self.token_has_expired = expires_at < now
            return True
