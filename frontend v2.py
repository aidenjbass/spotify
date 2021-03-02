# external module imports
import tkinter as tk
import webview


def web_launch():  # using the pywebiew module I am able to launch a lightweight chromium-based browser within python
    webview.create_window(
        title='Spotify Authentication',
        url='http://google.com',
        confirm_close=False
    )
    webview.start()


base = tk.Tk()  # root window

'''
Centers window on any display
'''
window_width = base.winfo_reqwidth()  # gets width of tk window
window_height = base.winfo_reqheight()  # gets height of tk window

posx = int(base.winfo_screenwidth() / 2.35 - window_width / 2)
posy = int(base.winfo_screenheight() / 3 - window_height / 2)

# position the window center of display
base.geometry('+{}+{}'.format(posx, posy))
# gives minimum size in px
base.config(height=500, width=500)
# disables ability to resize window
base.resizable(False, False)
'''
End
'''

'''
Beginning of widgets
'''
# variable setting
choice = tk.StringVar(base)
dropdown_option_GUI = None
search_field_GUI = None


# dictionary of options
choices = ['Artist', 'Album', 'Track']
choice.set('Option')  # set the default option

popupMenu = tk.OptionMenu(base, choice, *choices)

tk.Label(base, text="Choose an option from the list below").place(relx=0.5, rely=0.2, anchor='center')
popupMenu.place(relx=0.5, rely=0.3, anchor='center')


# on change dropdown value
# noinspection PyUnusedLocal
def change_dropdown(*args):
    global dropdown_option_GUI
    dropdown_option_GUI = str(choice.get().lower())
    search_field_label['text'] = f"What {dropdown_option_GUI} would you like to search for?"
    return dropdown_option_GUI


# link function to change dropdown
choice.trace('w', change_dropdown)

search_field_label = tk.Label(base, text="What would you like to search for?")
search_field_label.place(relx=0.5, rely=0.4, anchor='center')

search_field_entry = tk.Entry(base)
search_field_entry.place(relx=0.5, rely=0.5, anchor='center')


def get_search_field_entry():
    global search_field_GUI
    search_field_GUI = str(search_field_entry.get())
    return search_field_GUI


login = tk.Button(base, text="Optionally, login to your account", command=lambda: web_launch())
login.place(relx=0.5, rely=0.7, anchor='center')


def send_GUI_query_to_backend():
    get_search_field_entry()
    dropdown_option = dropdown_option_GUI
    search_field = search_field_GUI
    print(dropdown_option, search_field)
    return dropdown_option, search_field


execute = tk.Button(base, text="When ready to search, click me", command=lambda: send_GUI_query_to_backend())
execute.place(relx=0.5, rely=0.9, anchor='center')

base.mainloop()
