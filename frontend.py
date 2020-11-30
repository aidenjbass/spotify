import tkinter as tk


def get_search_field_from_frontend(button_input):
    # test function to interact tkinter with backend script Spotify.py
    if button_input == 'album':
        search_field = button_input
        print(search_field)
        return search_field
    elif button_input == 'artist':
        search_field = button_input
        print(search_field)
        return search_field
    elif button_input == 'track':
        search_field = button_input
        print(search_field)
        return search_field
    else:
        print('invalid')


'''
Start of GUI
'''

base = tk.Tk()  # root window

wWidth = base.winfo_reqwidth()  # gets width of tk window
wHeight = base.winfo_reqheight()  # gets height of tk window

posx = int(base.winfo_screenwidth() / 2 - wWidth / 2)
posy = int(base.winfo_screenheight() / 2 - wHeight / 2)

# position the window center of display
base.geometry('+{}+{}'.format(posx, posy))

# start of widgets
button_album = tk.Button(base, text='Select Album',
                         command=lambda: get_search_field_from_frontend(button_input='album'))
button_artist = tk.Button(base, text='Select Artist',
                          command=lambda: get_search_field_from_frontend(button_input='artist'))
button_track = tk.Button(base, text='Select Track',
                         command=lambda: get_search_field_from_frontend(button_input='track'))
button_album.pack()
button_artist.pack()
button_track.pack()

# end of widgets
base.mainloop()

'''
End of GUI
'''