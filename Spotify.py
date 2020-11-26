import base64
import datetime
import requests
from urllib.parse import urlencode

cid = '06f1f688ba144e21b3594f8dddc4a35c'
secret = 'bd81aa1b4e814cc7915c03839af073bd'


class ClientAuth(object):
    token = None
    token_expires_at = datetime.datetime.now()
    token_has_expired = True
    token_url = "https://accounts.spotify.com/api/token"

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
        else:
            client_credentials = f'{client_id}:{client_secret}'
            client_credentials_base64 = base64.b64encode(client_credentials.encode())
            return client_credentials_base64.decode()

    @staticmethod
    def get_token_data():
        return {
            'grant_type': 'client_credentials'
        }

    def get_token_header(self):
        client_credentials_base64 = self.get_client_credentials()
        return {
            'Authorization': f'Basic {client_credentials_base64}'
        }

    def authenticate(self):
        access_token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()
        r1 = requests.post(access_token_url, data=token_data, headers=token_headers)
        valid_request = r1.status_code in range(200, 299)
        if valid_request is False:
            raise Exception('Authetication failed')
        else:
            response_data = r1.json()
            now = datetime.datetime.now()
            token = response_data['access_token']
            expires_in = response_data['expires_in']  # in seconds
            expires_at = now + datetime.timedelta(seconds=expires_in)
            self.token = token
            self.token_expires_at = expires_at
            self.token_has_expired = expires_at < now
            return True

    def get_access_token(self):
        token = self.token
        expires_at = self.token_expires_at
        now = datetime.datetime.now()
        if expires_at < now:
            self.authenticate()
            return self.get_access_token()
        elif token is None:
            self.authenticate()
            return self.get_access_token()
        else:
            return token


class SearchEngine(object):
    CHANGEME = ClientAuth(cid, secret)
    CHANGEME.authenticate()
    token = CHANGEME.get_access_token()

    # print(token)

    header = {
        'Authorization': f'Bearer {token}'
    }

    # print(header)

    # noinspection PyMethodParameters,PyMethodMayBeStatic
    def get_type_query():
        option = None
        option_limit = 4
        while option not in range(1, 3):
            try:
                option = int(input('1. Album\n'
                                   '2. Artist\n'
                                   '3. Track \n'
                                   'Choose a number : '))
                if option >= option_limit:
                    print('Not an option')
                elif option == 1:
                    print('Selected Album')
                    type_query = 'album'
                    return type_query
                elif option == 2:
                    print('Selected Artist')
                    type_query = 'artist'
                    return type_query
                elif option == 3:
                    print('Selected Track')
                    type_query = 'track'
                    return type_query
                else:
                    pass
            except ValueError:
                print('Not an option')

    # noinspection PyMethodParameters,PyMethodMayBeStatic
    def get_search_field():
        search_field = str(input('What would you like to search for? : '))
        return search_field
    # function unfinished, will add string validation later on

    search_type_query = get_type_query()
    search_field_query = get_search_field()

    endpoint = 'https://api.spotify.com/v1/search'
    search_query = urlencode({'q': f'{search_field_query}', 'type': f'{search_type_query}', 'limit': '1'})
    lookup_url = f'{endpoint}?{search_query}'

    # print(search_query)
    # print(lookup_url)

    r2 = requests.get(lookup_url, headers=header)

    # print(r2.status_code)
    print(r2.json())
