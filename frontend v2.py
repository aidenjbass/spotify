# external module imports
import tkinter as tk
import webview

dropdown = ' '


def web_launch():  # using the pywebiew module I am able to launch a lightweight chromium-based browser within python
    webview.create_window(
        title='Spotify Authentication',
        url='http://google.com',
        confirm_close=True
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
# variable
choice = tk.StringVar(base)

# dictionary of options
choices = ['Artist', 'Album', 'Track']
choice.set('Option')  # set the default option

popupMenu = tk.OptionMenu(base, choice, *choices)

tk.Label(base, text="Choose an option from the list below").place(relx=0.5, rely=0.2, anchor='center')
popupMenu.place(relx=0.5, rely=0.3, anchor='center')


# on change dropdown value
# noinspection PyUnusedLocal
def change_dropdown(*args):
    global dropdown
    dropdown = str(choice.get().lower())
    print(dropdown)
    search_field_label['text'] = f"What {dropdown} would you like to search for?"
    return dropdown


# link function to change dropdown
choice.trace('w', change_dropdown)

# 'CHOICE' below needs to change when dropdown menu is changed
search_field_label = tk.Label(base, text="What would you like to search for?")
search_field_label.place(relx=0.5, rely=0.5, anchor='center')

search_field = tk.Entry(base)
search_field.place(relx=0.5, rely=0.6, anchor='center')

login = tk.Button(base, text="Optionally, login to your account", command=lambda: web_launch())
login.place(relx=0.5, rely=0.8, anchor='center')

base.mainloop()
