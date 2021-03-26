# external imports
import base64
import datetime
import io
import os
import tkinter as tk
from tkinter import font
from tkinter import messagebox
from urllib.parse import urlencode

import pandas as pd
import requests
import webview
from tabulate import tabulate

# project imports
import secrets

cid = secrets.spotify_cid
secret = secrets.spotify_csecret

# dict that converts musical key from numerical notation to lettered notation
# uses standard pitch class notation
music_key = {
    0: 'C',
    1: 'C#',
    2: 'D',
    3: 'D#',
    4: 'E',
    5: 'F',
    6: 'F#',
    7: 'G',
    8: 'G#',
    9: 'A',
    10: 'A#',
    11: 'B'
}

# dict that converts musical mode (major/minor) in numerical notation to lettered notation
# uses standard notation
music_mode = {
    0: 'Minor',
    1: 'Major'
}


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

    def print_track_audio_features(self, response_data, tracklist):
        # pandas option setting
        pd.set_option('display.max_columns', None)  # displays all columns
        pd.set_option('mode.chained_assignment', None)  # overwrites same dataframe rather than copies

        data = io.StringIO(tracklist)  # uses io to make comma separated string into csv

        # makes csv of track names with header 'name'
        df_track_names = pd.read_csv(
            data,
            sep='\n',
            names=['name']
        )
        df_track_names.index += 1  # adds 1 to index so index starts at 1

        track_features = self.get_track_info(response_data)  # gets track_features json
        df_track_features = pd.json_normalize(track_features['audio_features'])  # using pandas to convert json to df
        df_track_features.index += 1  # adds 1 to index so index starts at 1

        # merges df_track_names nad df_track_features into one dataframe
        df_track_info_merged = df_track_names.merge(
            df_track_features,
            how='outer',
            left_index=True,
            right_index=True
        )

        # list of all columns in dataframe, commented out columns not needed for scope of program
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
            # 'uri',
            # 'track_href',
            # 'analysis_url',
            'duration_ms',
            'time_signature'
        ]])

        # converts numerical key notation into lettered notation
        df_track_info_merged['key'] = df_track_info_merged['key'].map({
            0: 'C',
            1: 'C#',
            2: 'D',
            3: 'D#',
            4: 'E',
            5: 'F',
            6: 'F#',
            7: 'G',
            8: 'G#',
            9: 'A',
            10: 'A#',
            11: 'B'
        })

        # converts numerical modal notation into lettered notation
        df_track_info_merged['mode'] = df_track_info_merged['mode'].map({
            0: 'Minor',
            1: 'Major'
        })

        # rounds float values of 'danceablity', 'energy' to 1dp and 'tempo' to 0dp
        df_track_info_merged = df_track_info_merged.round({
            'danceability': 1,
            'energy': 1,
            'tempo': 0
        })

        # converts the track duration in milliseconds to HH:MM:SS format, creates new column 'track length'
        df_track_info_merged['Track Length'] = pd.to_datetime(
            df_track_info_merged['duration_ms'], unit='ms').dt.strftime('%H:%M:%S').str[:]

        # deletes column named 'duration_ms' from dataframe
        df_track_info_drop_duration = df_track_info_merged.drop(columns=['duration_ms'])

        # capitalizes all column header names
        df_track_info_caps = df_track_info_drop_duration.rename(str.capitalize, axis='columns')

        # renames 'time_signature' to 'Time Signature' and 'Track length' to 'Track Length'
        df_track_info_rename_ts = df_track_info_caps.rename(columns={
            'Time_signature': 'Time Signature',
            'Track length': 'Track Length'
        })

        # correctly formats time signature column
        df_track_info_rename_ts['Time Signature'] = df_track_info_rename_ts['Time Signature'].astype(str) + ' \\ 4'

        return df_track_info_rename_ts  # returns final dataframe

    @staticmethod
    def track_info_comparison(df):
        # finds rows with same key and mode, 'keep' parameter is set to false to keep all duplicates
        similar_key = df[df.duplicated(['Key', 'Mode'], keep=False)]
        # sorts similar_key according to alphabetical 'key'
        similar_key_sorted = similar_key.sort_values(by=['Key'])
        return similar_key_sorted  # returns edited dataframe of tracks that share key and mode with another track


'''
*** FRONTEND STARTS HERE ***
'''

base = tk.Tk()  # root window

padx = 10
pady = 10


def center_tkinter_window():  # Centers window on any display
    window_width = base.winfo_reqwidth()  # gets width of tk window
    window_height = base.winfo_reqheight()  # gets height of tk window

    posx = int(base.winfo_screenwidth() / 2.3 - window_width / 2)  # calculates x coordinate of window on launch
    posy = int(base.winfo_screenheight() / 2.8 - window_height / 2)  # calculates y coordinate of window on launch

    base.title("Spotify Song Feature Finder")
    base.geometry('+{}+{}'.format(posx, posy))  # position the window center of display
    base.config(height=500, width=500)  # gives minimum size in px
    base.resizable(False, False)  # disables ability to resize window if FALSE
    base.pack_propagate(0)  # ensures size is set by .config rather than the widgets themselves
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
popupMenu_label = tk.Label(
    base,
    text="Choose an option from the list below",
    font=('Segoe UI', 12, 'normal')
)
popupMenu_label.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)

popupMenu = tk.OptionMenu(base, choice, *choices)
popupMenu.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)

search_field_label = tk.Label(
    base,
    text="What option would you like to search for?",
    font=('Segoe UI', 12, 'normal')
)
search_field_label.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)

search_field_entry = tk.Entry(base)
search_field_entry.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)

login = tk.Button(
    base,
    text="Log in to your Spotify account",
    command=lambda: web_launch(),
    font=('Segoe UI', 12, 'normal'))
login.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)

instruction_label = tk.Label(
    base,
    text='or',
    font=('Segoe UI', 12, 'normal')
)
instruction_label.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)


execute = tk.Button(
    base,
    text='Continue',
    command=lambda: invoke_from_frontend(),
    font=('Segoe UI', 12, 'normal')
)
execute.pack(
    side=tk.TOP,
    padx=padx,
    pady=pady
)

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
            df_track_info = TrackInfo_invoke.print_track_audio_features(response_data, tracklist)
            df_similar_key = TrackInfo_invoke.track_info_comparison(df=df_track_info)
            output_results_to_GUI(df_track_info, df_similar_key)

        elif dropdown_option == 'album':
            response = SearchEngine_invoke.get_album_tracklist(response_search_query=search_2)  # gets response object
            response_data = response.json()  # parses as json format
            tracklist = SearchEngine_invoke.list_album_tracklist(response_data)  # gets a string list of tracks
            TrackInfo_invoke.get_album_tracklist_ids(response_data)  # gets ids for every track
            df_track_info = TrackInfo_invoke.print_track_audio_features(response_data, tracklist)
            df_similar_key = TrackInfo_invoke.track_info_comparison(df=df_track_info)
            output_results_to_GUI(df_track_info, df_similar_key)

        elif dropdown_option == 'track':
            response = SearchEngine_invoke.get_track(response_search_query=search_2)  # gets response object
            response_data = response.json()  # parses as json format
            tracklist = SearchEngine_invoke.list_track(response_data)  # gets a string list of tracks
            TrackInfo_invoke.get_track_id(response_data)  # gets ids for every track
            df_track_info = TrackInfo_invoke.print_track_audio_features(response_data, tracklist)
            df_similar_key = TrackInfo_invoke.track_info_comparison(df=df_track_info)
            output_results_to_GUI(df_track_info, df_similar_key)

        else:
            pass

    elif dropdown_option == 'option' and (search_field is None or search_field == ''):
        # warning popup if dropdown_option not sent and search_field not set
        tk.messagebox.showwarning(title='Warning', message="Option not chosen and search is invalid")

    elif search_field is None or search_field == '':
        # warning popup if search_field not set
        tk.messagebox.showwarning(title='Warning', message="Search invalid")

    elif dropdown_option == 'option':
        # warning popup if dropdown_option not set
        tk.messagebox.showwarning(title='Warning', message="Option not chosen")

    else:
        pass


def get_download_path():
    # Returns the default downloads path for linux or windows
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')


def output_results_to_GUI(df_track_info_merged, df_similar_key):
    # outputs results from dataframe to tkinter in tabulated format
    show_result_window = tk.Button(
        base,
        text="Click me to open results",
        command=lambda: make_newWindow(),
        font=('Segoe UI', 12, 'normal')
    )
    show_result_window.pack(
        side=tk.TOP,
        padx=padx,
        pady=pady
    )

    # sets font to be used in this window, courier is used because it is mono width
    courierNew = font.Font(family='Courier New', size=12, weight='normal')

    def make_newWindow():  # creates a new window when show_result_window is clicked
        def export_table_1_to_csv():
            directory = f'{get_download_path()}\\df_track_info.csv'
            df_track_info_merged.to_csv(f'{directory}', index=False)

        def export_table_2_to_csv():
            directory = f'{get_download_path()}\\df_track_similar_keys.csv'
            df_similar_key.to_csv(f'{directory}', index=False)

        # tabulate option setting
        tabulate.PRESERVE_WHITESPACE = False
        # creates a new tkinter window called newWindow
        newWindow = tk.Toplevel(base)
        # using tabulate to format dataframe in pretty format for tkinter
        if dropdown_option == 'artist' or 'album':
            GUI_output_full_result = tk.Label(
                newWindow,
                text=(tabulate(
                    df_track_info_merged,
                    showindex=False,
                    headers='keys',
                    tablefmt='psql'
                )),
                font=courierNew
            )

            GUI_output_export_button_1 = tk.Button(
                newWindow,
                text="Output to downloads folder in csv format",
                command=lambda: export_table_1_to_csv(),
                font=courierNew
            )

            GUI_output_following_songs = tk.Label(
                newWindow,
                text="The following songs with the same key and mode are suitable to be remixed together"
                     "\n"
                     "Those with equal or similar 'danceability' and 'energy' values are even more suitable"
                     "",
                font=courierNew
            )

            # using tabulate to format dataframe in pretty format for tkinter
            GUI_output_similar_key = tk.Label(
                newWindow,
                text=(tabulate(
                    df_similar_key,
                    showindex=False,
                    headers='keys',
                    tablefmt='psql'
                )),
                font=courierNew
            )

            GUI_output_export_button_2 = tk.Button(
                newWindow,
                text="Output to downloads folder in csv format",
                command=lambda: export_table_2_to_csv(),
                font=courierNew
            )

            width = (GUI_output_full_result.winfo_reqwidth())  # gets width of table
            # gets height of all widgets combined
            height = (
                    GUI_output_full_result.winfo_reqheight() +
                    GUI_output_export_button_1.winfo_reqheight() +
                    GUI_output_similar_key.winfo_reqheight() +
                    GUI_output_following_songs.winfo_reqheight() +
                    GUI_output_export_button_2.winfo_reqheight()
            )

            newWindow.geometry('%dx%d' % (width, height))  # sets px size of window
            newWindow.resizable(False, False)  # disables ability to resize window if FALSE
            newWindow.wm_attributes('-topmost', 1)  # always on top

            # "packs" widgets into grid in relation to side, in this case top down
            GUI_output_full_result.pack(side=tk.TOP)
            GUI_output_export_button_1.pack(side=tk.TOP)
            GUI_output_following_songs.pack(side=tk.TOP)
            GUI_output_similar_key.pack(side=tk.TOP)
            GUI_output_export_button_2.pack(side=tk.TOP)

        if dropdown_option == 'track':
            GUI_output_full_result = tk.Label(
                newWindow,
                text=(tabulate(
                    df_track_info_merged,
                    showindex=False,
                    headers='keys',
                    tablefmt='psql'
                )),
                font=courierNew
            )

            GUI_output_export_button_1 = tk.Button(
                newWindow,
                text="Output to downloads folder in csv format",
                command=lambda: export_table_1_to_csv(),
                font=courierNew
            )

            width = (GUI_output_full_result.winfo_reqwidth())  # gets width of table
            # gets height of all widgets combined
            height = (
                    GUI_output_full_result.winfo_reqheight() +
                    GUI_output_export_button_1.winfo_reqheight()
            )

            newWindow.geometry('%dx%d' % (width, height))  # sets px size of window
            newWindow.resizable(False, False)  # disables ability to resize window if FALSE
            newWindow.wm_attributes('-topmost', 1)  # always on top

            # "packs" widgets into grid in relation to side, in this case top down
            GUI_output_full_result.pack(side=tk.TOP)
            GUI_output_export_button_1.pack(side=tk.TOP)


base.mainloop()

# todo add artist/album name to table
