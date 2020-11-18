import base64
import datetime
import requests


class SpotifyAPI(object):
    class ClientAuth(object):
        token = None
        token_expires_at = datetime.datetime.now()
        token_has_expired = True

        client_id = '06f1f688ba144e21b3594f8dddc4a35c'
        client_secret = 'bd81aa1b4e814cc7915c03839af073bd'

        token_url = "https://accounts.spotify.com/api/token"

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
            return token

    class UserAuth(object):
        pass

    class SearchPython(object):
        pass


self = SpotifyAPI.ClientAuth()
print(SpotifyAPI.ClientAuth.get_access_token(self))
