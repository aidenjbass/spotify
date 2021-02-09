import tkinter as tk
import webview


def web_launch():
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
# variable
choice = tk.StringVar(base)

# dictionary of options
choices = ['Artist', 'Album', 'Track']
choice.set('Option')  # set the default option

popupMenu = tk.OptionMenu(base, choice, *choices)

tk.Label(base, text="Choose an option from the list below").place(relx=0.5, rely=0.2, anchor='center')
popupMenu.place(relx=0.5, rely=0.3, anchor='center')


# on change dropdown value
def change_dropdown_search_type(*args):
    print(choice.get().lower())
    return choice.get().lower()


# link function to change dropdown
choice.trace('w', change_dropdown_search_type)

# 'CHOICE' below needs to change when dropdown menu is changed
search_field_label = tk.Label(base, text=f'What CHOICE would you like to search for?')
search_field_label.place(relx=0.5, rely=0.5, anchor='center')

search_field = tk.Entry(base)
search_field.place(relx=0.5, rely=0.6, anchor='center')

login = tk.Button(base, text='Optionally, login to your account', command=lambda: web_launch())
login.place(relx=0.5, rely=0.8, anchor='center')


base.mainloop()
