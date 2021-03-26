# external imports
import base64
import datetime
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlencode

import requests
import webview

# project imports
import secrets

cid = secrets.spotify_cid
secret = secrets.spotify_csecret


class ClientAuth(object):  # this class is just for the client authentication

    # constant setting
    token = None
    token_expires_at = datetime.datetime.now()  # gets time NOW
    token_has_expired = True
    token_url = 'https://accounts.spotify.com/api/token'  # endpoint given by API

    # client_id and and client_secret are now constants stored in the external file secrets.py
    client_id = None
    client_secret = None

    def __init__(self, client_id, client_secret):  # intialises self, passing client_id and client_secret into class
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):  # forms client_credentials as required by API
        # returns the base64 string
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise Exception("client_id or client_secret not set")
        else:  # encodes the credentials in base64 encoding rather than UTF, which is required by the API
            client_credentials = f'{client_id}:{client_secret}'  # f string that combines two vars together
            client_credentials_base64 = base64.b64encode(client_credentials.encode())  # base64 encodes client_creds
            return client_credentials_base64.decode()

    @staticmethod  # a static method that simply stores the grant_type required by the API
    def get_token_data():
        return {
            'grant_type': 'client_credentials'
        }

    def get_token_header(self):  # combines the authorization type and header data needed by the API
        return {
            'Authorization': f'Basic {self.get_client_credentials()}'
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
        if valid_request is False:  # raises exception in console
            raise Exception("Authentication failed")
        else:
            response_data = json_response_token.json()
            now = datetime.datetime.now()  # gets time now
            token = response_data['access_token']  # response_data is a json, gets access_token item
            expires_in = response_data['expires_in']  # in seconds, will typically give a value of 3600 seconds
            expires_at = now + datetime.timedelta(seconds=expires_in)  # calculates time at which token expires
            self.token = token  # passes to class
            self.token_expires_at = expires_at  # passes to class
            self.token_has_expired = expires_at < now  # gives boolean
            return True

    def get_access_token(self):  # actually gets token when function is called outside of class
        token = self.token
        expires_at = self.token_expires_at  # gives the DD/MM/YYYY HH:MM:SS format of when token expires
        now = datetime.datetime.now()  # gets time now
        if expires_at < now:  # if when the token expires is before NOW, token is invalid and must be re-authenticated
            self.authenticate()
            return self.get_access_token()
        elif token is None:  # if the token variable is 'None' or 'Null', must be re-authenticated
            self.authenticate()
            return self.get_access_token()
        else:  # otherwise, if the token is valid, not None and is later than time NOW, re-authentication is not needed
            return token


class SearchEngine(object):
    InvokeAuthFromClient = ClientAuth(cid, secret)  # initializes ClientAuth and passes cid and secret in

    def __init__(self):
        pass

    @staticmethod
    def list_artist_top_10_GUI(response_data):  # lists an artists top ten songs
        form_top = ''
        for i in range(10):  # TODO change to range(len) as some users may not have 10 songs released
            top = response_data['tracks'][i]['name']  # response_data is json, gets name of each track
            form_top = str(f'{form_top}{top}\n')  # iterates on previous string
        return form_top

    @staticmethod
    def list_album_tracklist(response_data):  # lists names of all tracks in an album
        form_tracklist = ''
        for i in range(len(response_data['items'])):  # gets i amount of tracks in album, loops i amount of times
            tracklist = response_data['items'][i]['name']  # response_data is json, gets name of each track
            form_tracklist = str(f'{form_tracklist}{tracklist}\n')  # iterates on previous string
        return form_tracklist

    @staticmethod
    def list_track(response_data):  # lists name of individual track
        track_name = response_data['name']  # response_data is json, gets name
        return track_name

    def get_search_header(self):  # forms the HTTP header needed for search engine
        return {
            'Authorization': f'Bearer {self.InvokeAuthFromClient.get_access_token()}'
        }

    @staticmethod
    def get_search_endpoint():  # returns URL endpoint needed for search
        endpoint = 'https://api.spotify.com/v1/search'  # API endpoint to search API
        return endpoint

    # variable setting
    search_field_query = None
    search_type_query = None

    def make_search_query(self, search_field_query, search_type_query):
        # parses search_query with option category and chosen search from option category
        # creates dict style ready for HTTP requests using urlencode
        search_query = urlencode({
            'q': f'{search_field_query}',
            'type': f'{search_type_query}',
            'limit': '1'
        })
        lookup_url = f'{self.get_search_endpoint()}?{search_query}'  # forms URL of HTTP request
        # interacts with Spotify API and retrieves the top search query
        response_search_query = requests.get(
            lookup_url,
            headers=self.get_search_header()
        )
        return response_search_query

    def form_header_results(self):  # forms header for track(s) 'audio_features' endpoint
        return {
            'Accept': 'application/json',
            'Content_Type': 'application/json',
            'Authorization': f'Bearer {self.InvokeAuthFromClient.get_access_token()}'
        }

    def get_artist_top_tracks(self, response_search_query):
        response_artist_search = response_search_query.json()
        artist_id = response_artist_search['artists']['items'][0]['id']  # gets artist id
        # GET https://api.spotify.com/v1/artists/{id}/top-tracks
        endpoint = 'https://api.spotify.com/v1/artists'  # endpoint for artist search
        # URL encoded dict for HTTP request, not required but advised
        market = urlencode({
            'market': 'US'
        })
        artist_top_tracks_url = f'{endpoint}/{artist_id}/top-tracks?{market}'  # forms URL
        # makes HTTP request to return an artists up to top 10
        artist_top_tracks_request = requests.get(
            artist_top_tracks_url,
            headers=self.form_header_results()
        )
        return artist_top_tracks_request  # returns artist top 10 tracks

    def get_album_tracklist(self, response_search_query):
        response_album_search = response_search_query.json()
        album_id = response_album_search['albums']['items'][0]['id']  # gets id of album
        # GET https://api.spotify.com/v1/albums/{id}/tracks
        endpoint = 'https://api.spotify.com/v1/albums'  # album endpoint given by API
        # URL encoded dict for HTTP request, not required but advised
        market = urlencode({
            'market': 'US'
        })
        album_listing_url = f'{endpoint}/{album_id}/tracks?{market}'  # forms URL
        # makes HTTP request to return album information
        album_listing_request = requests.get(
            album_listing_url,
            headers=self.form_header_results()
        )
        return album_listing_request  # returns album tracklist

    def get_track(self, response_search_query):
        response_track_search = response_search_query.json()
        track_id = response_track_search['tracks']['items'][0]['id']  # gets track id
        # GET https://api.spotify.com/v1/tracks/{id}
        endpoint = 'https://api.spotify.com/v1/tracks/'  # tracks endpoint given by API
        # URL encoded dict for HTTP request, not required but advised
        market = urlencode({
            'market': 'US'
        })
        track_listing_url = f'{endpoint}{track_id}?{market}'  # forms URL
        # makes HTTP request to return track information
        track_listing_request = requests.get(
            track_listing_url,
            headers=self.form_header_results()
        )
        return track_listing_request  # returns track


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

        return form_top_ids  # returns a string of an artist top 10 track UID's separated by comma

    @staticmethod
    def get_album_tracklist_ids(response_data):
        form_tracklist_id = ''
        for i in range(len(response_data['items'])):
            tracklist_ids = response_data['items'][i]['id']
            form_tracklist_id += str(tracklist_ids + ',')

        return form_tracklist_id  # returns a string of an albums track UID's separated by comma

    @staticmethod
    def get_track_id(response_data):
        track_id = response_data['id']
        return track_id  # returns an individual track id

    def form_header(self):  # forms header used in requests to audio_features endpoint of API
        return {
            'Accept': 'application/json',
            'Content_Type': 'application/json',
            'Authorization': f'Bearer {self.InvokeAuthFromClient.get_access_token()}'
        }

    def get_track_info(self, response_data):
        track_ids = ''
        # GET https://api.spotify.com/v1/audio-features
        if dropdown_option == 'artist':  # if artist passes response_data to artist function
            track_ids = self.get_artist_top_track_ids(response_data)
        elif dropdown_option == 'album':  # if album passes response_data to album function
            track_ids = self.get_album_tracklist_ids(response_data)
        elif dropdown_option == 'track':  # if track passes response_data to track function
            track_ids = self.get_track_id(response_data)
        else:
            pass
        endpoint = 'https://api.spotify.com/v1/audio-features?'  # endpoint for audio_features
        track_info_url = f'{endpoint}ids={track_ids}'  # forms URL
        # makes request for audio_features object json
        track_info_request = requests.get(
            track_info_url,
            headers=self.form_header()
        )

        return track_info_request.json()


'''
*** FRONTEND STARTS HERE ***
'''

base = tk.Tk()  # root window


def center_tkinter_window():  # Centers window on any display
    window_width = base.winfo_reqwidth()  # gets width of tk window
    window_height = base.winfo_reqheight()  # gets height of tk window

    posx = int(base.winfo_screenwidth() / 2.3 - window_width / 2)  # calculates x coordinate of window on launch
    posy = int(base.winfo_screenheight() / 2.8 - window_height / 2)  # calculates y coordinate of window on launch

    base.geometry('+{}+{}'.format(posx, posy))  # position the window center of display
    base.config(height=(base.winfo_reqheight() + 400), width=(base.winfo_reqwidth() + 400))  # gives minimum size in px
    base.resizable(False, False)  # disables ability to resize window if FALSE
    # base.wm_attributes('-topmost', 1)  # if enable, window is always on top


center_tkinter_window()

choice = tk.StringVar(base)  # variable setting
choices = ['Artist', 'Album', 'Track']  # dictionary of options
choice.set('Option')  # set the default option


# IGNORE IDE COMMENTS
# noinspection PyUnusedLocal
def get_change_dropdown(*args):  # on change dropdown value
    dropdown_option_GUI = str(choice.get().lower())  # gets selected list option from dropdown_menu
    # edits search_field_label every change
    # If artist, search_field_label reads 'What artist would you like to search for?'
    # If album, search_field_label reads 'What album would you like to search for?'
    # If track, search_field_label reads 'What track would you like to search for?'
    search_field_label['text'] = f"What {dropdown_option_GUI} would you like to search for?"
    return dropdown_option_GUI


choice.trace('w', get_change_dropdown)  # link function to change dropdown

# Main window widgets
popupMenu_label = tk.Label(base, text="Choose an option from the list below")
popupMenu_label.place(relx=0.5, rely=0.1, anchor='center')

popupMenu = tk.OptionMenu(base, choice, *choices)
popupMenu.place(relx=0.5, rely=0.16, anchor='center')

search_field_label = tk.Label(base, text="What would you like to search for?")
search_field_label.place(relx=0.5, rely=0.35, anchor='center')

search_field_entry = tk.Entry(base)
search_field_entry.place(relx=0.5, rely=0.4, anchor='center')

login = tk.Button(base, text="Log in to your Spotify account", command=lambda: web_launch())
login.place(relx=0.5, rely=0.55, anchor='center')

instruction_label = tk.Label(base, text='or')
instruction_label.place(relx=0.5, rely=0.65, anchor='center')

execute = tk.Button(base, text="Continue", command=lambda: invoke_from_frontend())
execute.place(relx=0.5, rely=0.75, anchor='center')

# variable setting
dropdown_option = None
search_field = None


def web_launch():  # using the pywebiew module to launch a lightweight chromium-based browser within python
    webview.create_window(
        title="Spotify User Authentication",
        url='http://accounts.spotify.com',
        confirm_close=False
    )
    webview.start()


def get_search_field_entry():  # gets current input into search_field_entry
    search_field_GUI = str(search_field_entry.get())
    return search_field_GUI  # returns string


def send_GUI_query_to_backend():  # gets current dropdown menu option selected and currently inputted search_field
    global dropdown_option, search_field
    dropdown_option = get_change_dropdown()
    search_field = get_search_field_entry()
    return dropdown_option, search_field


def invoke_from_frontend():  # all interaction between backend and frontend passes through here
    send_GUI_query_to_backend()
    if search_field is not None and search_field != '' and dropdown_option != 'option':
        SearchEngine_invoke = SearchEngine()  # intializes SearchEngine class
        TrackInfo_invoke = TrackInfo()  # initializes TrackInfo class
        # passes search_field and dropdown_option from send_GUI_query_to_backend to make_search_query
        search_2 = SearchEngine_invoke.make_search_query(
            search_field_query=search_field,
            search_type_query=dropdown_option
        )
        if dropdown_option == 'artist':
            response = SearchEngine_invoke.get_artist_top_tracks(response_search_query=search_2)  # gets response object
            response_data = response.json()  # parses as json format
            tracklist = SearchEngine_invoke.list_artist_top_10_GUI(response_data)  # gets a string list of tracks
            TrackInfo_invoke.get_artist_top_track_ids(response_data)  # gets ids for every track

        elif dropdown_option == 'album':
            response = SearchEngine_invoke.get_album_tracklist(response_search_query=search_2)  # gets response object
            response_data = response.json()  # parses as json format
            tracklist = SearchEngine_invoke.list_album_tracklist(response_data)  # gets a string list of tracks
            TrackInfo_invoke.get_album_tracklist_ids(response_data)  # gets ids for every track

        elif dropdown_option == 'track':
            response = SearchEngine_invoke.get_track(response_search_query=search_2)  # gets response object
            response_data = response.json()  # parses as json format
            tracklist = SearchEngine_invoke.list_track(response_data)  # gets a string list of tracks
            TrackInfo_invoke.get_track_id(response_data)  # gets ids for every track
        else:
            pass
    elif dropdown_option == 'option' and (search_field is None or search_field == ''):
        # warning popup if dropdown_option not sent and search_field not set
        tk.messagebox.showwarning(title='Warning', message='Option not chosen and search is invalid')
    elif search_field is None or search_field == '':
        # warning popup if search_field not set
        tk.messagebox.showwarning(title='Warning', message="Search invalid")
    elif dropdown_option == 'option':
        # warning popup if dropdown_option not set
        tk.messagebox.showwarning(title='Warning', message="Option not chosen")
    else:
        pass


base.mainloop()


def output_results_to_GUI():
    # outputs results from dataframe to tkinter in tabulated format
    show_result_window = tk.Button(base, text="Click me to open results")
    show_result_window.place(relx=0.5, rely=0.9, anchor='center')
