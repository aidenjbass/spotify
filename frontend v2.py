import tkinter as tk
import webview


def web_test():
    webview.create_window(
        title='Spotify Authentication',
        url='http://google.com',
        confirm_close=False
    )
    webview.start()


base = tk.Tk()  # root window

'''
Centers code on any display
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
choice.set('Artist')  # set the default option

popupMenu = tk.OptionMenu(base, choice, *choices)

tk.Label(base, text="Choose An Option").place(relx=0.4, rely=0.2, anchor='center')
popupMenu.place(relx=0.7, rely=0.2, anchor='center')


# on change dropdown value
def change_dropdown(*args):
    print(choice.get().lower())
    return choice.get().lower()


# link function to change dropdown
choice.trace('w', change_dropdown)

tk.Button(base, text='Login to your account', command=lambda: web_test()).place(relx=0.5, rely=0.4, anchor='center')

base.mainloop()
