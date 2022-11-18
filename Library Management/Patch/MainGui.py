import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview

from BorrowingPerson import BorrowingPerson
from main import *

cnx = mysql.connector.connect(**{'user': 'sqluser', 'password': 'password', 'host': 'localhost', 'db': 'library'})


class MainGUI:
    def __init__(self, master):
        self.parent = master
        # Set frame for the whole thing
        self.parent.title("Library Management System")
        self.frame = Frame(self.parent, width=650, height= 600)
        self.frame.grid(row=0, column=0)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_propagate(False)

        # Parameter Initialization
        self.search_string = None
        self.data = None
        self.borrowerId = None
        self.bookForCheckOutIsbn = None

        # Frame for the welcome message and header
        self.HeaderFrame = Frame(self.frame)
        self.HeaderFrame.grid(row=0, column=0, sticky=N)
        self.HeaderFrame.grid_rowconfigure(0, weight=1)
        self.HeaderFrame.grid_columnconfigure(0, weight=1)

        # # Label for the welcome message
        self.HeaderLabel = Label(self.HeaderFrame, text='What Book Do You Want?')
        self.HeaderLabel.grid(row=0, column=0)
        self.HeaderLabel.grid_rowconfigure(0, weight=10)
        self.HeaderLabel.grid_columnconfigure(0, weight=10)

        self.MajorFunctions = Frame(self.frame)
        self.MajorFunctions.grid(row=3, column=0, sticky=N)
        self.MajorFunctions.grid_rowconfigure(3, weight=1)
        self.checkOutBtn = Button(self.MajorFunctions, text="Check Out Book", command=self.check_out)
        self.checkOutBtn.grid(row=0, column=0, padx=10, pady=10)
        self.checkOutBtn.grid_rowconfigure(0, weight=1)
        self.checkOutBtn.grid_columnconfigure(0, weight=1)
        self.checkInBtn = Button(self.MajorFunctions, text="Check In Book", command=self.check_in)
        self.checkInBtn.grid(row=0, column=1, padx=10, pady=10)
        self.checkOutBtn.grid_rowconfigure(0, weight=1)
        self.checkOutBtn.grid_columnconfigure(1, weight=1)
        self.updateFinesBtn = Button(self.MajorFunctions, text="Updates Fines", command=self.update_fines)
        self.updateFinesBtn.grid(row=1, column=0, padx=10, pady=10)
        self.payFinesBtn = Button(self.MajorFunctions, text="Pay Fines", command=self.pay_fines)
        self.payFinesBtn.grid(row=1, column=1, padx=10, pady=10)
        self.changeDayBtn = Button(self.MajorFunctions, text="Change Day", command=self.change_day)
        self.changeDayBtn.grid(row=1, column=2, padx=10, pady=10)
        self.addBorrowerBtn = Button(self.MajorFunctions, text="Add New Borrower", command=self.add_borrower)
        self.addBorrowerBtn.grid(row=0, column=2, padx=10, pady=10)

        # Label for the searchbox
        self.SearchLabel = Label(self.HeaderFrame, text='')
        self.SearchLabel.grid(row=1, column=0)
        self.SearchLabel.grid_rowconfigure(1, weight=10)
        self.SearchLabel.grid_columnconfigure(0, weight=10)

        # Search Frame
        self.SearchFrame = Frame(self.frame)
        self.SearchFrame.grid(row=1, column=0, sticky=N)
        self.SearchFrame.grid_rowconfigure(1, weight=1)
        # self.SearchFrame.grid_columnconfigure(0, weight=1)
        self.SearchLabel = Label(self.SearchFrame, text='Search')
        self.SearchLabel.grid(row=0, column=0)
        self.SearchLabel.grid_rowconfigure(0, weight=1)
        # self.SearchLabel.grid_columnconfigure(0, weight=1)
        self.SearchTextBox = Entry(self.SearchFrame, text='Enter search string here...', width=70)
        self.SearchTextBox.grid(row=1, column=0)
        self.SearchTextBox.grid_rowconfigure(1, weight=1)
        self.SearchButton = Button(self.SearchFrame, text='Search', command=self.search)
        self.SearchButton.grid(row=2, column=0)
        self.SearchButton.grid_rowconfigure(2, weight=1)

        # Search Result Frame
        self.ActiveArea = Frame(self.frame)
        self.ActiveArea.grid(row=2, column=0, sticky=N)
        self.ActiveArea.grid_rowconfigure(2, weight=1)
        # self.ResultTreeview = Treeview(self.ActiveArea, columns=["ISBN", "Book Title", "Author(s)", "Availability"])
        self.ResultTreeview = Treeview(self.ActiveArea, columns=["ISBN", "Book Title", "Availability"])
        self.ResultTreeview.grid(row=1, column=1)
        self.ResultTreeview.grid_rowconfigure(0, weight=1)
        self.ResultTreeview.heading('#0', text="ISBN")
        self.ResultTreeview.heading('#1', text="Book Title")
        # self.ResultTreeview.heading('#2', text="Author(s)")
        self.ResultTreeview.heading('#2', text="Availability")
        self.ResultTreeview.bind('<ButtonRelease-1>', self.selectBookForCheckout)

        # Interaction Frame


    def change_day(self):
        global todays_date
        todays_date = todays_date + timedelta(days=1)
        messagebox.showinfo("Date",todays_date.date())
        print(todays_date)

    def search(self):
        self.search_string = self.SearchTextBox.get()
        cursor = cnx.cursor()
        #
        # cursor.execute("select BOOK.isbn, BOOK.title, AUTHORS.fullname from BOOK join BOOK_AUTHORS on "
        #                "BOOK.isbn = BOOK_AUTHORS.isbn join AUTHORS on BOOK_AUTHORS.author_id = AUTHORS.author_id "
        #                "where BOOK.title like concat('%', '" + self.search_string + "', '%') or "
        #                                                                             "AUTHORS.fullname like concat('%', '" + self.search_string + "', '%') or "
        #                                                                                                            or                            "BOOK.isbn like concat('%', '" + self.search_string + "', '%')")
        #
        #
        #
        search_item = "'%" +self.search_string+"%'"
        cursor.execute("SELECT isbn,title from book where title like" + search_item)
        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
        """
        View data on Treeview method.
        """
        self.ResultTreeview.delete(*self.ResultTreeview.get_children())
        for elem in self.data:
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT EXISTS(SELECT Isbn from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(elem[0]) + "')")
            result = cursor.fetchall()
            if result == [(0,)]:
                availability = "Available"
            else:
                cursor = cnx.cursor()
                cursor.execute(
                    "SELECT BOOK_LOANS.Date_in from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(elem[0]) + "'")
                result = cursor.fetchall()
                if result[-1][0] is None:
                    availability = "Not Available"
                else:
                    availability = "Available"
            self.ResultTreeview.insert('', 'end', text=str(elem[0]),
                                       values=(elem[1], availability))

    def selectBookForCheckout(self, a):
        curItem = self.ResultTreeview.focus()
        self.bookForCheckOutIsbn = self.ResultTreeview.item(curItem)['text']

    def check_out(self):
        if self.bookForCheckOutIsbn is None:
            messagebox.showinfo("Attention!", "Select Book First!")
            return None
        self.borrowerId = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT Card_id from BORROWER WHERE Card_id = '" + str(self.borrowerId) + "')")
        result = cursor.fetchall()

        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower not in Database!")
            return None
        else:
            count = 0
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT BOOK_LOANS.Date_in from BOOK_LOANS WHERE BOOK_LOANS.Card_id = '" + str(self.borrowerId) + "'")
            result = cursor.fetchall()
            for elem in result:
                if elem[0] is None:
                    count += 1
            if count >= 3:
                messagebox.showinfo("Not Allowed!", "Borrower has loaned 3 books already!")
                return None
            else:
                cursor = cnx.cursor()
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                cursor.execute(
                    "INSERT INTO BOOK_LOANS (ISBN, Card_id, Date_out, Due_date) VALUES ('" + self.bookForCheckOutIsbn + "', '" + self.borrowerId + "', '" + str(
                        todays_date) + "', '" + str(todays_date + timedelta(days=14)) + "')")
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                cnx.commit()
                cursor = cnx.cursor()
                cursor.execute("SELECT MAX(Loan_Id) FROM BOOK_LOANS")
                result = cursor.fetchall()
                loan_id = result[0][0]
                cursor.execute(
                    "INSERT INTO FINES (Loan_Id, fine_amt, paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
                cnx.commit()
                messagebox.showinfo("Done", "Book Loaned Out!")

    def check_in(self):

        self.checkInWindow = Toplevel(self.parent)
        self.checkInWindow.title("Check In Here")
        self.app = CheckIn(self.checkInWindow)

    def update_fines(self):
        cursor = cnx.cursor()
        cursor.execute("SELECT BOOK_LOANS.Loan_Id, BOOK_LOANS.Date_in, BOOK_LOANS.Due_date FROM BOOK_LOANS")
        result = cursor.fetchall()
        for record in result:
            date_in = record[1]
            date_due = record[2]
            if date_in is None:
                date_in = todays_date
            diff = date_in.date - date_due.date
            if diff.days > 0:
                fine = int(diff.days) * 0.25
            else:
                fine = 0
            cursor = cnx.cursor()
            cursor.execute(
                "UPDATE FINES SET FINES.fine_amt = '" + str(fine) + "' WHERE FINES.Loan_Id = '" + str(record[0]) + "'")
            cnx.commit()
        messagebox.showinfo("Info", "Generated Fines")

    def pay_fines(self):
        self.newPayFinesWindow = Toplevel(self.parent)
        self.newPayFinesWindow.title("Fine!!")
        self.app1 = PayFines(self.newPayFinesWindow)

    def add_borrower(self):
        self.newBorrowerWindow = Toplevel(self.parent)
        self.newBorrowerWindow.title("Borrowing Person New")
        self.newapp = BorrowingPerson(self.newBorrowerWindow)
