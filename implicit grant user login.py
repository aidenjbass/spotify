# external imports
import requests

# project imports
import secrets

cid = secrets.spotify_cid

token_url = 'https://accounts.spotify.com/authorize'
client_id = cid

get_client_id = {'client_id': client_id}

get_response_type = {'response_type': 'token'}

get_redirect_uri = {'redirect_uri': 'https://blazingcreeperx.github.io/'}

get_show_dialog = {'show_dialog': 'True'}

access_token_url = token_url
token_header = (
    get_client_id,
    get_response_type,
    get_redirect_uri,
    get_show_dialog
)
r1 = requests.get(access_token_url, headers=token_header)
print(r1)

