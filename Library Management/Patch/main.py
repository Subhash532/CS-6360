import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview
import tkinter.ttk as ttk
from ttkthemes import ThemedTk

from MainGui import *
from PayFines import *
from BorrowingPerson import *
from CheckIn import *

global cnx
cnx = mysql.connector.connect(host='localhost',
                              database='library',
                              user='sqluser',
                              password='password',
                              )
cursor = None
todays_date = datetime.today()

if __name__ == '__main__':
    root = ThemedTk(theme="radiance")
    tool = MainGUI(root)
    root.mainloop()
