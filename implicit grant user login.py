# project imports
import secrets

cid = secrets.spotify_cid


class ImplicitGrant(object):
    # constant setting
    client_id = cid

    def __init__(self, client_id):
        self.client_id = client_id

    def get_client_id(self):
        return {
            'client_id': self.client_id
        }

    @staticmethod
    def get_response_type():
        return {
            'response_type': 'token'
        }

    @staticmethod
    def get_redirect_uri():
        return {
            'redirect_uri': 'https://blazingcreeperx.github.io/'
        }

    @staticmethod
    def get_show_dialog():
        return {
            'show_dialog': 'True'
        }
