import tkinter as tk
from tkinter import filedialog


def get_file_path(saveas=True, defaultextension=".txt", filetypes=(("Text Documents", "*.txt"),), **kwargs):
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-alpha", 0)
    if saveas:
        path = filedialog.asksaveasfilename(defaultextension=defaultextension, filetypes=filetypes, **kwargs)
    else:
        path = filedialog.askopenfilename(defaultextension=defaultextension, filetypes=filetypes, **kwargs)

    root.destroy()
    return path
