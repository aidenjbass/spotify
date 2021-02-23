from tkinter import StringVar

import tkinter as tk
from tkinter import *

secs = ['Subject', 'Difficulty', 'Percent', 'Grade', 'Pass']

master = Tk()
v = StringVar(master)
v.set(secs[0])


def on_option_change(event):
    global lab2
    lab2.destroy()
    lab2 = tk.Label(master, text=v.get())
    lab2.grid(row=2, column=1)


w = OptionMenu(master, v, *secs, command=on_option_change)
w.grid(row=1, column=0)
lab1 = tk.Label(master, text='Current value:')
lab1.grid(row=2, column=0, sticky=E)
lab2 = tk.Label(master, text=secs[0])
lab2.grid(row=2, column=1, sticky=W)
mainloop()
