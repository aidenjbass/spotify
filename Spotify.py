# external imports
import base64
import datetime
import requests
from urllib.parse import urlencode

# project imports
import secrets

cid = secrets.spotify_cid
secret = secrets.spotify_csecret


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
            raise Exception('Authentication failed')
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

    def get_access_token(self):
        token = self.token
        expires_at = self.token_expires_at  # gives the DD/MM/YYYY HH:MM:SS format of when token expires
        now = datetime.datetime.now()
        if expires_at < now:  # if when the token expires is before NOW, token is invalid and must be re-authenticated
            self.authenticate()
            return self.get_access_token()
        elif token is None:  # if the token variable is 'None' or 'Null', must be re-authenticated
            self.authenticate()
            return self.get_access_token()
        else:  # otherwise, if the token is valid, not None and is later than time NOW, re-authentication is not needed
            return token


class SearchEngine(object):
    InvokeAuthFromClient = ClientAuth(cid, secret)
    InvokeAuthFromClient.authenticate()
    token = InvokeAuthFromClient.get_access_token()

    # print(token)

    header = {
        'Authorization': f'Bearer {token}'
    }

    # print(header)

    # IDE comments, IGNORE
    # noinspection PyMethodParameters,PyMethodMayBeStatic
    def get_type_query():
        # once the GUI is created, this function will become redundant
        # for now it is a text based input that the GUI will accomplish instead
        # defining constants
        option = None
        option_limit = 4
        while option not in range(1, 3):  # any input that is not an int between 1 and 3 is invalid
            try:
                option = int(input('1. Album \n'
                                   '2. Artist \n'
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
            except ValueError:  # if invalid int input raises ValueError and returns to loop start
                print('Not an option')

    # IDE comments, IGNORE
    # noinspection PyMethodParameters,PyMethodMayBeStatic
    def get_search_field():
        # this function asks the user what they would like to search for after selecting what type they would like
        # to search for
        # example,
        # if type_query = album then valid search_field = 'Abbey Road'
        # if type_query = artist then valid search_field = 'Ed Sheeran'
        # if type_query = track then valid search_field = 'Bohemian Rhapsody'
        # function unfinished, will add string validation later on
        search_field = str(input('What would you like to search for? : '))
        return search_field

    search_type_query = get_type_query()
    search_field_query = get_search_field()
    # search_field_query = frontend.get_search_field_from_frontend()

    endpoint = 'https://api.spotify.com/v1/search'  # API endpoint to search API
    # parses search_query with option category and chosen search from option category
    search_query = urlencode({'q': f'{search_field_query}',
                              'type': f'{search_type_query}',
                              'limit': '1'})
    lookup_url = f'{endpoint}?{search_query}'

    # print(search_query)
    # print(lookup_url)

    r2 = requests.get(lookup_url, headers=header)  # interacts with Spotify API and retrieves the top search query

    # print(r2.status_code)
    print(r2.json())
