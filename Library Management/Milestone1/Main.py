import mysql.connector
from tkinter import *
import tkinter as tk 
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
from mysql.connector import Error

connection = mysql.connector.connect(host="localhost",user="sqluser", passwd="password",database="library")
cursor = connection.cursor()

root= Tk()
root.title("Library")
root.geometry = ("800x625")

SEARCHTERM = StringVar()
# ============================ENTRY=======================================

searchTerm = Entry(textvariable=SEARCHTERM, font=('arial', 14))
searchTerm.grid(row=0, column=0, sticky=W+E, padx=5, pady=2)

# ============================BUTTONS=======================================

btn_search = Button(text="SEARCH", bg="#66ffff")
btn_search.grid(row=0, column=1, sticky=E+W,padx=0, pady=2)
btn_add = Button(text="+Add New", bg="#66ff66")
btn_add.grid(row=0, column=2, sticky=W+E, padx=15, pady=2)
btn_delete = Button(text="Delete", bg="#f7735c")
btn_delete.grid(row=0, column=3, sticky=E+W,padx=15, pady=2)

SearchForm = Frame(root, width=300)
SearchForm.columnconfigure(0, weight=3)
SearchForm.columnconfigure(1, weight=1)
TableMargin = Frame(root, width=300)

# ============================ Db Connection Verification  =======================================
try:
    if connection.is_connected():
        Info = connection.get_server_info()
        print("Connected to MySQL", Info)
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("Connected to the given database:",record)
except Error as e:
    print("An Error while Connecting to MySQL",e)

# ============================ End of Db Connection =================================

cursor.execute("SELECT Card_id,Ssn,Bname,Address,Phone FROM borrower limit 0,30")
i=10
for borrower in cursor: 
    for j in range(len(borrower)):
        e = Entry(root, width=40, fg='blue') 
        e.grid(row=i, column=j) 
        e.insert(END, borrower[j])
    i=i+1

if __name__ == '__main__':
    root.mainloop()
    cursor.close()
    connection.close()
    print("MySQL connection is closed")
    
