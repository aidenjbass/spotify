# external imports
from urllib.parse import urlencode
import base64
import datetime
import tkinter as tk
from tkinter import messagebox
import requests
import webview
import pandas as pd
import io
from tabulate import tabulate

# project imports
import secrets

cid = secrets.spotify_cid
secret = secrets.spotify_csecret


class ClientAuth(object):  # this class is just for the client authentication

    # constant setting
    token = None
    token_expires_at = datetime.datetime.now()
    token_has_expired = True
    token_url = 'https://accounts.spotify.com/api/token'

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
            raise Exception("client_id or client_secret not set")
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
        json_response_token = requests.post(
            access_token_url,
            data=token_data,
            headers=token_headers
        )
        valid_request = json_response_token.status_code in range(200, 299)  # anything outside this range is invalid
        if valid_request is False:
            raise Exception("Authentication failed")
        else:
            response_data = json_response_token.json()
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

    def __init__(self):
        pass

    @staticmethod
    def list_artist_top_10_GUI(response_data):
        form_top = ''
        for i in range(10):
            top = response_data['tracks'][i]['name']
            form_top = str(f'{form_top}{top}\n')
        return form_top

    @staticmethod
    def list_album_tracklist(response_data):
        form_tracklist = ''
        for i in range(len(response_data['items'])):
            tracklist = response_data['items'][i]['name']
            form_tracklist = str(f'{form_tracklist}{tracklist}\n')
        return form_tracklist

    @staticmethod
    def list_track(response_data):
        track_name = response_data['name']
        print(track_name)
        return track_name

    def get_search_header(self):
        return {
            'Authorization': f'Bearer {self.InvokeAuthFromClient.get_access_token()}'
        }

    @staticmethod
    def get_search_endpoint():
        endpoint = 'https://api.spotify.com/v1/search'  # API endpoint to search API
        return endpoint

    search_field_query = None
    search_type_query = None

    def make_search_query(self, search_field_query, search_type_query):
        # parses search_query with option category and chosen search from option category
        search_query = urlencode({
            'q': f'{search_field_query}',
            'type': f'{search_type_query}',
            'limit': '1'
        })
        lookup_url = f'{self.get_search_endpoint()}?{search_query}'
        # interacts with Spotify API and retrieves the top search query
        response_search_query = requests.get(
            lookup_url,
            headers=self.get_search_header()
        )
        return response_search_query

    def form_header_results(self):  # shouldn't be static
        return {
            'Accept': 'application/json',
            'Content_Type': 'application/json',
            'Authorization': f'Bearer {self.InvokeAuthFromClient.get_access_token()}'
        }

    def get_artist_top_tracks(self, response_search_query):
        response_artist_search = response_search_query.json()
        artist_id = response_artist_search['artists']['items'][0]['id']
        # GET https://api.spotify.com/v1/artists/{id}/top-tracks
        endpoint = 'https://api.spotify.com/v1/artists'
        market = urlencode({
            'market': 'US'
        })
        artist_top_tracks_url = f'{endpoint}/{artist_id}/top-tracks?{market}'
        artist_top_tracks_request = requests.get(
            artist_top_tracks_url,
            headers=self.form_header_results()
        )
        return artist_top_tracks_request

    def get_album_tracklist(self, response_search_query):
        response_album_search = response_search_query.json()
        album_id = response_album_search['albums']['items'][0]['id']
        # GET https://api.spotify.com/v1/albums/{id}/tracks
        endpoint = 'https://api.spotify.com/v1/albums'
        market = urlencode({
            'market': 'US'
        })
        album_listing_url = f'{endpoint}/{album_id}/tracks?{market}'
        album_listing_request = requests.get(
            album_listing_url,
            headers=self.form_header_results()
        )
        return album_listing_request

    def get_track(self, response_search_query):
        response_track_search = response_search_query.json()
        track_id = response_track_search['tracks']['items'][0]['id']
        # GET https://api.spotify.com/v1/tracks/{id}
        endpoint = 'https://api.spotify.com/v1/tracks/'
        market = urlencode({
            'market': 'US'
        })
        track_listing_url = f'{endpoint}{track_id}?{market}'
        track_listing_request = requests.get(
            track_listing_url,
            headers=self.form_header_results()
        )
        return track_listing_request


class TrackInfo(object):
    InvokeAuthFromClient = ClientAuth(cid, secret)

    def __init__(self):
        pass

    @staticmethod
    def get_artist_top_track_ids(response_data):
        form_top_ids = ''
        for i in range(10):
            top_ids = response_data['tracks'][i]['id']
            form_top_ids += str(top_ids + ',')

        # print(form_top_ids)
        return form_top_ids

    @staticmethod
    def get_album_tracklist_ids(response_data):
        form_tracklist_id = ''
        for i in range(len(response_data['items'])):
            tracklist_ids = response_data['items'][i]['id']
            form_tracklist_id += str(tracklist_ids + ',')

        # print(form_tracklist_id)
        return form_tracklist_id

    @staticmethod
    def get_track_id(response_data):
        track_id = response_data['id']
        return track_id

    def form_header(self):
        return {
            'Accept': 'application/json',
            'Content_Type': 'application/json',
            'Authorization': f'Bearer {self.InvokeAuthFromClient.get_access_token()}'
        }

    def get_track_info(self, response_data):
        track_ids = ''
        # GET https://api.spotify.com/v1/audio-features
        if dropdown_option == 'artist':
            track_ids = self.get_artist_top_track_ids(response_data)
        elif dropdown_option == 'album':
            track_ids = self.get_album_tracklist_ids(response_data)
        elif dropdown_option == 'track':
            track_ids = self.get_track_id(response_data)
        else:
            pass
        endpoint = 'https://api.spotify.com/v1/audio-features?'
        track_info_url = f'{endpoint}ids={track_ids}'
        track_info_request = requests.get(
            track_info_url,
            headers=self.form_header()
        )
        # print(track_info_request.json())
        return track_info_request.json()

    def print_track_audio_features(self, response_data, tracklist):
        # pandas option setting
        pd.set_option('display.max_columns', None)

        # tabulate option setting
        tabulate.PRESERVE_WHITESPACE = True

        track_features = self.get_track_info(response_data)

        data = io.StringIO(tracklist)
        df_track_names = pd.read_csv(
            data,
            sep='\n',
            names=['name']
        )
        df_track_names.index += 1

        df_track_features = pd.json_normalize(track_features['audio_features'])
        df_track_features.index += 1

        df_track_info_merged = df_track_names.merge(
            df_track_features,
            how='outer',
            left_index=True,
            right_index=True
        )

        df_track_info_merged = (df_track_info_merged[[
            'name',
            'danceability',
            'energy',
            'key',
            # 'loudness',
            'mode',
            # 'speechiness',
            # 'acousticness',
            # 'instrumentalness',
            # 'liveness',
            # 'valence',
            'tempo',
            # 'id',
            'duration_ms',
            'time_signature'
        ]])

        print(df_track_info_merged)
        return df_track_info_merged


'''
*** FRONTEND STARTS HERE ***
'''

base = tk.Tk()  # root window


def center_tkinter_window():  # Centers window on any display
    window_width = base.winfo_reqwidth()  # gets width of tk window
    window_height = base.winfo_reqheight()  # gets height of tk window

    posx = int(base.winfo_screenwidth() / 3.8 - window_width / 2)
    posy = int(base.winfo_screenheight() / 4 - window_height / 2)

    base.geometry('+{}+{}'.format(posx, posy))  # position the window center of display
    base.config(height=800, width=1200)  # gives minimum size in px
    base.resizable(True, True)  # disables ability to resize window if FALSE
    # base.wm_attributes('-topmost', 1)  # always on top


center_tkinter_window()

'''
Beginning of widgets
'''

choice = tk.StringVar(base)  # variable setting
choices = ['Artist', 'Album', 'Track']  # dictionary of options
choice.set('Option')  # set the default option


# on change dropdown value
# noinspection PyUnusedLocal
def get_change_dropdown(*args):
    dropdown_option_GUI = str(choice.get().lower())
    search_field_label['text'] = f"What {dropdown_option_GUI} would you like to search for?"
    return dropdown_option_GUI


choice.trace('w', get_change_dropdown)  # link function to change dropdown

popupMenu_label = tk.Label(base, text="Choose an option from the list below")
popupMenu_label.place(relx=0.2, rely=0.2, anchor='center')

popupMenu = tk.OptionMenu(base, choice, *choices)
popupMenu.place(relx=0.2, rely=0.25, anchor='center')

search_field_label = tk.Label(base, text="What would you like to search for?")
search_field_label.place(relx=0.2, rely=0.4, anchor='center')

search_field_entry = tk.Entry(base)
search_field_entry.place(relx=0.2, rely=0.45, anchor='center')

login = tk.Button(base, text="Optionally, login to your account", command=lambda: web_launch())
login.place(relx=0.2, rely=0.7, anchor='center')

execute = tk.Button(base, text="When ready to search, click me", command=lambda: invoke_from_frontend())
execute.place(relx=0.2, rely=0.9, anchor='center')

dropdown_option = None
search_field = None


def web_launch():  # using the pywebiew module to launch a lightweight chromium-based browser within python
    webview.create_window(
        title="Spotify Authentication",
        url='http://google.com',
        confirm_close=False
    )
    webview.start()


def output_results_to_GUI(df_track_info_merged):
    show_result_window = tk.Button(base, text="Click me to open results", command=lambda: make_newWindow())
    show_result_window.place(relx=0.5, rely=0.5, anchor='center')

    def make_newWindow():
        with pd.option_context('expand_frame_repr', True):
            newWindow = tk.Toplevel(base)
            newWindow.geometry("%dx%d" % (base.winfo_reqwidth(), base.winfo_reqheight()))
            GUI_output = tk.Label(
                newWindow,
                text=(tabulate(
                    df_track_info_merged,
                    showindex=False,
                    headers=df_track_info_merged.columns,
                )),
                padx=None, pady=None,
                justify='right'
            )
            GUI_output.place(relx=0.5, rely=0.5, anchor='center')


def get_search_field_entry():
    search_field_GUI = str(search_field_entry.get())
    return search_field_GUI


def send_GUI_query_to_backend():
    global dropdown_option, search_field
    dropdown_option = get_change_dropdown()
    search_field = get_search_field_entry()
    return dropdown_option, search_field


def invoke_from_frontend():
    send_GUI_query_to_backend()
    # if search_field has * - + it is invalid and raise error, new input ask from user, otherwise continue
    if search_field is not None and search_field != '' and dropdown_option != 'option':
        SearchEngine_invoke = SearchEngine()
        TrackInfo_invoke = TrackInfo()
        search_2 = SearchEngine_invoke.make_search_query(
            search_field_query=search_field,
            search_type_query=dropdown_option
        )
        if dropdown_option == 'artist':
            response = SearchEngine_invoke.get_artist_top_tracks(response_search_query=search_2)
            response_data = response.json()
            tracklist = SearchEngine_invoke.list_artist_top_10_GUI(response_data)
            TrackInfo_invoke.get_artist_top_track_ids(response_data)

            df_track_info_merged = TrackInfo_invoke.print_track_audio_features(response_data, tracklist)
            output_results_to_GUI(df_track_info_merged)

        elif dropdown_option == 'album':
            response = SearchEngine_invoke.get_album_tracklist(response_search_query=search_2)
            response_data = response.json()
            tracklist = SearchEngine_invoke.list_album_tracklist(response_data)
            TrackInfo_invoke.get_album_tracklist_ids(response_data)

            df_track_info_merged = TrackInfo_invoke.print_track_audio_features(response_data, tracklist)
            output_results_to_GUI(df_track_info_merged)

        elif dropdown_option == 'track':
            response = SearchEngine_invoke.get_track(response_search_query=search_2)
            response_data = response.json()
            SearchEngine_invoke.list_track(response_data)
            TrackInfo_invoke.get_track_id(response_data)
            TrackInfo_invoke.get_track_info(response_data)
        else:
            pass
    elif search_field is None or search_field != '':
        tk.messagebox.showwarning(title="Warning", message="Search invalid")
    elif dropdown_option == 'option':
        tk.messagebox.showwarning(title="Warning", message="Option not chosen")
    else:
        pass


base.mainloop()
