import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview
import tkinter.ttk as ttk
from ttkthemes import ThemedTk


from GUI import *


global conn
conn = mysql.connector.connect(**{'user': 'sqluser', 'password': 'password', 'host': 'localhost', 'db': 'library'})


if __name__ == '__main__':
    gui()
    mainloop()
