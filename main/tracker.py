from tkinter import *
import os
import tkinter.font as tkFont
from helper import *

root = Tk()
root.title("Workload Tracker")

# when testing on terminal, use these lines to get cwd
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
cwd = __location__ + "\\data\\"

# when creating the exe, use this line to get cwd
# cwd = "data\\"

root.iconbitmap(cwd + "icon.ico")

# font settings
combobox_font = tkFont.Font(family="微软雅黑",size=16)
root.option_add("*TCombobox*Listbox*Font", combobox_font)

main_page(root)

root.mainloop()