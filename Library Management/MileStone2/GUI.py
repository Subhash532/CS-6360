import tkinter as tk
from datetime import date
from tkinter import *
from tkinter import ttk, simpledialog
from tkinter import messagebox
from tkinter.ttk import Treeview

import mysql.connector

from main import *

conn = mysql.connector.connect(**{'user': 'sqluser', 'password': 'password', 'host': 'localhost', 'db': 'library'})

global today
today = date.today()


class gui(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        self.geometry('850x600')
        self.title("Library Management System")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (HomePage, book_availability, borrower_page, checkin_page, payfines_page, show_fines):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


#     Home Page
class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        Header_label = Label(self, text="Librarian View", background="yellow")
        Header_label.grid(row=3, column=2)
        Header_label.grid_rowconfigure(0, weight=1)
        ttk.Button(self, text="Book Availability", width=20,
                   command=lambda: controller.show_frame(book_availability)).grid(row=3,
                                                                                  column=3,
                                                                                  sticky=E + W,
                                                                                  padx=15,
                                                                                  pady=2)
        ttk.Button(self, text="Check-In", width=20, command=lambda: controller.show_frame(checkin_page)).grid(row=3,
                                                                                                              column=4,
                                                                                                              sticky=E + W,
                                                                                                              padx=15,
                                                                                                              pady=2)

        ttk.Button(self, text="Add Borrower", width=20, command=lambda: controller.show_frame(borrower_page)).grid(
            row=4,
            column=3,
            sticky=E + W,
            padx=15,
            pady=2)
        ttk.Button(self, text="Pay Fines", width=20, command=lambda: controller.show_frame(payfines_page)).grid(row=4,
                                                                                                                column=4,
                                                                                                                sticky=E + W,
                                                                                                                padx=15,
                                                                                                                pady=2)
        ttk.Button(self, text="Show Fines", width=20, command=lambda: controller.show_frame(show_fines)).grid(row=5,
                                                                                                              column=3,
                                                                                                              sticky=E + W,
                                                                                                              padx=15,
                                                                                                              pady=2)
        ttk.Button(self, text="Update Fines", width=20, command=lambda: update_fine()).grid(row=5,
                                                                                            column=4,
                                                                                            sticky=E + W,
                                                                                            padx=15,
                                                                                            pady=2)


#   End of Home Page


#    Book Search Page
class book_availability(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.bookIsbn = None
        self.borrowerId = None

        search_text_label = Label(self, text="Please Provide Search item format:Isbn,Title,Author", background="yellow")
        search_text_label.grid(row=0, column=2)
        search_text_label.grid_rowconfigure(0, weight=1)
        search_text = ttk.Entry(self, width=50)
        search_text.grid(row=1, column=2)
        search_text.grid_rowconfigure(1, weight=1)

        SearchButton = ttk.Button(self, text='Search', command=lambda: self.SearchBook(search_text))
        SearchButton.grid(row=2, column=2)
        SearchButton.grid_rowconfigure(2, weight=1)

        CheckOutBtn = ttk.Button(self, text="CheckOut", width=30, command=lambda: self.BookCheckOut())
        CheckOutBtn.grid(row=20, column=2)
        BackButton = ttk.Button(self, text="Back To HomePage", width=40,
                                command=lambda: controller.show_frame(HomePage))
        BackButton.grid(row=22, column=2)
        BackButton.grid_rowconfigure(22, weight=1)
        ActiveArea = Frame(self)
        ActiveArea.grid(row=12, column=2, sticky=N)
        ActiveArea.grid_rowconfigure(12, weight=1)

        self.ResultTreeview = Treeview(ActiveArea, columns=["ISBN", "Book Title", "Author(s)", "Availability"])
        self.ResultTreeview.grid(row=1, column=1)
        self.ResultTreeview.grid_rowconfigure(1, weight=1)
        self.ResultTreeview.heading('#0', text="ISBN")
        self.ResultTreeview.heading('#1', text="Book Title")
        self.ResultTreeview.heading('#2', text="Author(s)")
        self.ResultTreeview.heading('#3', text="Book-Availability")
        self.ResultTreeview.bind('<ButtonRelease-1>', self.CheckoutBook)

    def CheckoutBook(self, a):
        curItem = self.ResultTreeview.focus()
        self.bookIsbn = self.ResultTreeview.item(curItem)['text']

    def BookCheckOut(self):

        if self.bookIsbn is None:
            generate_message("Attention! , Select Book First!")
            return None
        self.borrowerId = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT Card_ID from BORROWER WHERE Card_ID = '" + str(self.borrowerId) + "')")
        result = cursor.fetchall()

        if result == [(0,)]:
            generate_message("Error! , Borrower not in Database!")
            return None
        else:
            count = 0
            cursor = conn.cursor()
            cursor.execute(
                "SELECT BOOK_LOANS.Date_in from BOOK_LOANS WHERE BOOK_LOANS.Card_id = '" + str(self.borrowerId) + "'")
            result = cursor.fetchall()
            for elem in result:
                if elem[0] is None:
                    count += 1
            if count >= 3:
                generate_message("Not Allowed!, Borrower has loaned 3 books already!")
                return None
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM BOOK_LOANS WHERE Isbn= '" + self.bookIsbn + "' and date_in is null")
                cnt = cursor.fetchall()
                if cnt == [(1,)]:
                    generate_message("Not Allowed!, Book has already loaned out !")
                    return None
                else:
                    cursor = conn.cursor()
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                    cursor.execute(
                        "INSERT INTO BOOK_LOANS (ISBN, Card_id, Date_out, Due_date) VALUES ('" + self.bookIsbn + "', '" + self.borrowerId + "', '" + str(
                            today) + "', '" + str(today + timedelta(days=14)) + "')")
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                    conn.commit()
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(Loan_Id) FROM BOOK_LOANS")
                    result = cursor.fetchall()
                    loan_id = result[0][0]
                    cursor.execute(
                        "INSERT INTO FINES (Loan_Id, fine_amt, paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
                    conn.commit()
                    generate_message("Done, Book Loaned Out!")

    def SearchBook(self, search_text):
        temp = search_text.get().split(',')
        if len(temp) == 3:
            search_string_isbn = temp[0].strip()
            search_string_title = temp[1].strip()
            search_string_author = temp[2].strip()
        elif len(temp) == 2:
            search_string_isbn = temp[0].strip()
            search_string_title = temp[1].strip()
            search_string_author = ''
        elif len(temp) == 1:
            search_string_isbn = temp[0].strip()
            search_string_title = ''
            search_string_author = ''
        else:
            search_string_isbn = ''
            search_string_title = ''
            search_string_author = ''

        if conn.is_connected():
            print("Db connected, Searching book")
        cursor = conn.cursor()

        q1 = "select BOOK.isbn, BOOK.title, group_concat(AUTHORS.name) from BOOK join BOOK_AUTHORS on BOOK.isbn = " \
             "BOOK_AUTHORS.isbn join AUTHORS on BOOK_AUTHORS.author_id = AUTHORS.author_id where "
        if search_string_title == '':
            q2 = ""
        else:
            q2 = " BOOK.title like concat('%', '" + search_string_title + "', '%')  "

        if search_string_author == '':
            q3 = ""
        else:
            q3 = " AUTHORS.name like concat('%', '" + search_string_author + "', '%') "

        if search_string_isbn == '':
            q4 = ""
        else:
            q4 = " BOOK.isbn like concat('%', '" + search_string_isbn + "', '%')"

        q5 = " group by BOOK.isbn,BOOK.title;"

        if search_string_isbn == '' and search_string_author == '' and search_string_title == '':
            q_final = "select BOOK.isbn, BOOK.title, AUTHORS.name from BOOK join BOOK_AUTHORS on BOOK.isbn = " \
                      "BOOK_AUTHORS.isbn join AUTHORS on BOOK_AUTHORS.author_id = AUTHORS.author_id where BOOK.title " \
                      "like concat('%', ' ', '%') or AUTHORS.name like concat('%', ' ', '%') or BOOK.isbn like " \
                      "concat('%', ' ', '%') group by BOOK.isbn,BOOK.title; "
        else:
            if q2 == '' and (q3 != '' and q4 != ''):
                q_final = q1 + q3 + "and" + q4 + q5
            elif q3 == '' and (q2 != '' and q4 != ''):
                q_final = q1 + q2 + "and" + q4 + q5
            elif q4 == '' and (q3 != '' and q2 != ''):
                q_final = q1 + q2 + "and" + q3 + q5
            elif q2 != '' and (q3 == '' and q4 == ''):
                q_final = q1 + q2 + q5
            elif q3 != '' and (q2 == '' and q4 == ''):
                q_final = q1 + q3 + q5
            elif q4 != '' and (q3 == '' and q2 == ''):
                q_final = q1 + q4 + q5
            elif q3 != '' and q2 != '' and q3 != '':
                q_final = q1 + q2 + "or" + q3 + "or" + q4 + q5
        print(q_final)
        cursor.execute(q_final)

        data = cursor.fetchall()
        self.view_data(data)

    def view_data(self, data):

        self.ResultTreeview.delete(*self.ResultTreeview.get_children())

        for elem in data:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT EXISTS(SELECT BOOK_LOANS.isbn from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(elem[0]) + "')")
            result = cursor.fetchall()
            if str(result) == '[(0,)]':
                availability = "Available"
            else:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT BOOK_LOANS.Date_in,BOOK_LOANS.due_date from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(
                        elem[0]) + "'")
                result = cursor.fetchall()
                if result[-1][0] is None:
                    availability = "Not Available"
                else:
                    availability = "Available"
            self.ResultTreeview.insert('', 'end', text=str(elem[0]), values=(str(elem[1]), str(elem[2]), availability))


#   End of Book Search Page


#   Borrower Page
class borrower_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        titleLabel = Label(self, text="Enter Details")
        titleLabel.grid(row=0, column=0, padx=20, pady=20)
        fnameLabel = Label(self, text="First Name").grid(row=1, column=0, padx=10, pady=5)
        fnameTB = Entry(self)
        fnameTB.grid(row=1, column=2, padx=10, pady=5)
        lnameLabel = Label(self, text="Last Name").grid(row=3, column=0, padx=10, pady=5)
        lnameTB = Entry(self)
        lnameTB.grid(row=3, column=2, padx=10, pady=5)
        ssnLabel = Label(self, text="SSN").grid(row=5, column=0, padx=10, pady=5)
        ssnTB = Entry(self)
        ssnTB.grid(row=5, column=2, padx=10, pady=5)
        addressLabel = Label(self, text="Street Address").grid(row=7, column=0, padx=10, pady=5)
        addressTB = Entry(self)
        addressTB.grid(row=7, column=2, padx=10, pady=5)
        cityLabel = Label(self, text="City").grid(row=9, column=0, padx=10, pady=5)
        cityTB = Entry(self)
        cityTB.grid(row=9, column=2, padx=10, pady=5)
        stateLabel = Label(self, text="State").grid(row=11, column=0, padx=10, pady=5)
        stateTB = Entry(self)
        stateTB.grid(row=11, column=2, padx=10, pady=5)
        numberLabel = Label(self, text="Phone Number").grid(row=13, column=0, padx=10, pady=5)
        numberTB = Entry(self)
        numberTB.grid(row=13, column=2, padx=10, pady=5)
        addBtn = Button(self, text="Add", width=30,
                        command=lambda: addBorrower(ssnTB, addressTB, cityTB, stateTB, fnameTB, lnameTB, numberTB))
        addBtn.grid(row=14, column=0, padx=10, pady=5)
        clrBtn = Button(self, text="Clear", width=30,
                        command=lambda: clear_text())
        clrBtn.grid(row=14, column=2, padx=10, pady=5)
        BackButton = ttk.Button(self, text="Back To HomePage", width=40,
                                command=lambda: controller.show_frame(HomePage))
        BackButton.grid(row=18, column=2)
        BackButton.grid_rowconfigure(2, weight=1)

        def clear_text():
            fnameTB.delete(0, END)
            lnameTB.delete(0, END)
            ssnTB.delete(0, END)
            addressTB.delete(0, END)
            cityTB.delete(0, END)
            stateTB.delete(0, END)
            numberTB.delete(0, END)


#   End of Borrower Page


#   CheckIn Page
class checkin_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.bookForCheckInID = None
        self.search_string = None
        self.data = None
        searchLabel = ttk.Label(self, text="Search here: Borrower ID, Borrower Name or ISBN")
        searchLabel.grid(row=0, column=0, padx=20, pady=20)
        search_text = ttk.Entry(self)
        search_text.grid(row=1, column=0)
        self.search_string = search_text.get()
        searchBtn = ttk.Button(self, text="Search", command=lambda: self.search_book_loans(search_text.get()))
        searchBtn.grid(row=2, column=0)
        self.table = Treeview(self, columns=["Loan ID", "ISBN", "Borrower ID", "Title"])
        self.table.grid(row=3, column=0)
        self.table.heading('#0', text="Loan ID")
        self.table.heading('#1', text="ISBN")
        self.table.heading('#2', text="Borrower ID")
        self.table.heading('#3', text="Book Title")
        self.table.bind('<ButtonRelease-1>', self.select_book_for_checkin)
        checkInBtn = ttk.Button(self, text="Check In", command=self.check_in)
        checkInBtn.grid(row=4, column=0)
        BackButton = ttk.Button(self, text="Back To HomePage", width=40,
                                command=lambda: controller.show_frame(HomePage))
        BackButton.grid(row=30, column=0)
        BackButton.grid_rowconfigure(5, weight=1)

    def search_book_loans(self, search_s):
        search_b = "'%" + search_s + "%'"
        cursor = conn.cursor()
        cursor.execute(
            "select BOOK_LOANS.Loan_Id, BOOK_LOANS.ISBN, BOOK_LOANS.Card_id, BOOK.title, BOOK_LOANS.Date_in "
            "from BOOK_LOANS "
            "join BORROWER on BOOK_LOANS.Card_id = BORROWER.Card_ID "
            "join BOOK on BOOK_LOANS.ISBN = BOOK.ISBN "
            "where Borrower.Card_ID like " + search_b + " or Borrower.Bname like " + search_b + " or Book.Isbn like " + search_b)

        self.data = cursor.fetchall()
        for row in self.data:
            print(row)
        self.view_data()

    def view_data(self):
        self.table.delete(*self.table.get_children())
        for elem in self.data:
            if elem[4] is None:
                self.table.insert('', 'end', text=str(elem[0]), values=(elem[1], elem[2], elem[3]))

    def select_book_for_checkin(self, a):
        curItem = self.table.focus()
        self.bookForCheckInID = self.table.item(curItem)['text']
        print("Loan Id to be checked out:" + self.bookForCheckInID)

    def check_in(self):
        today = date.today()
        if self.bookForCheckInID is None:
            generate_message("Attention!, Select Book to Check In First!")
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT BOOK_LOANS.Date_in FROM BOOK_LOANS WHERE BOOK_LOANS.Loan_Id = '" + str(
            self.bookForCheckInID) + "'")
        result = cursor.fetchall()
        if result[0][0] is None:
            cursor.execute("UPDATE BOOK_LOANS SET BOOK_LOANS.Date_in = '" + str(
                today) + "' WHERE BOOK_LOANS.Loan_Id = '"
                           + str(self.bookForCheckInID) + "'")
            conn.commit()
            generate_message("Done, Book Checked In Successfully!")

        else:
            return None


#   End of CheckIn Page


#   PayFines Page
class payfines_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.v = StringVar()
        ttk.Label(self, text="Enter Borrower ID").grid(row=0, column=0, padx=20, pady=20)
        borrowerEntry = ttk.Entry(self)
        borrowerEntry.grid(row=1, column=2, padx=20, pady=20)
        showfinesbtn = ttk.Button(self, text="Show Fines", command=lambda: self.show_fines(borrowerEntry))
        showfinesbtn.grid(row=2, column=2, padx=20, pady=20)
        fineLabel = ttk.Label(self, textvariable=self.v)
        fineLabel.grid(row=3, column=2, padx=20, pady=20)
        payfinesbtn = ttk.Button(self, text="Pay Fine", command=lambda: self.pay_fine(borrowerEntry))
        payfinesbtn.grid(row=4, column=2, padx=20, pady=20)
        BackButton = ttk.Button(self, text="Back To HomePage", width=40,
                                command=lambda: controller.show_frame(HomePage))
        BackButton.grid(row=20, column=2)
        BackButton.grid_rowconfigure(5, weight=1)

    def pay_fine(self, borrowerEntry):
        borrower_id = borrowerEntry.get()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT Card_ID FROM BORROWER WHERE BORROWER.Card_ID = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            generate_message("Error Borrower does not exist!!")
        else:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT FINES.Loan_Id,BOOK_LOANS.date_in FROM FINES JOIN BOOK_LOANS ON FINES.Loan_Id = BOOK_LOANS.Loan_Id WHERE "
                "BOOK_LOANS.Card_id = '" + str(
                    borrower_id) + "'")
            result = cursor.fetchall()
            for elem in result:
                if elem[1] is None:
                    generate_message("All Books are not returned,Remaining fines are paid")
                else:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE FINES SET FINES.paid = 1 WHERE FINES.Loan_Id = '" + str(elem[0]) + "'")
                    conn.commit()
            generate_message("Fines Paid Successfully!")

    def show_fines(self, borrowerEntry):
        total_fine = 0
        borrower_id = borrowerEntry.get()
        if borrower_id == '':
            generate_message("Please Provide Borrower Id")
        else:
            print("BorrowerID = " + str(borrower_id))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT EXISTS(SELECT Card_ID FROM BORROWER WHERE BORROWER.Card_ID = '" + str(borrower_id) + "')")
            result = cursor.fetchall()
            if result == [(0,)]:
                generate_message("Error,Borrower does not exist!!")
                # print("Empty")
            else:
                cursor.execute(
                    "SELECT FINES.fine_amt, FINES.paid FROM FINES JOIN BOOK_LOANS ON FINES.Loan_Id = BOOK_LOANS.Loan_Id "
                    "WHERE BOOK_LOANS.Card_id = '" + str(
                        borrower_id) + "'")
                result = cursor.fetchall()
                total_fine = 0
                for elem in result:
                    if elem[1] == 0:
                        total_fine += float(elem[0])
                fine_d = format(total_fine, '.2f')
            self.v.set("Fine: $ " + str(fine_d))


#   End of Pay Fines Page


# Message Generator
def generate_message(msg):
    tk.messagebox.showinfo("LMS", msg)


# end of Message Generator


# Add Borrower
def addBorrower(ssn, Address, City, State, Fname, Lname, PhNo):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(Card_ID) from BORROWER")
    new_card_no = int(cursor.fetchall()[0][0]) + 1
    new_card_no = 'ID00' + str(new_card_no)
    new_ssn = str(ssn.get())[0:3] + "-" + str(ssn.get())[3:5] + "-" + str(ssn.get())[5:]

    if len(Fname.get()) == 0 or len(Lname.get()) == 0 or not Fname.get().isalpha or not Lname.get().isalpha:
        Fname.delete(0, END)
        Lname.delete(0, END)
        messagebox.showerror("Validation Error", "Enter correct Name!")
        return None

    if len(ssn.get()) != 9 or not (ssn.get().isdigit()):
        ssn.delete(0, END)
        messagebox.showerror("Validation Error", "Enter correct value of SSN!")
        return None

    if len(Address.get()) == 0 or len(City.get()) == 0 or len(
            State.get()) == 0 or not City.get().isalpha() or not State.get().isalpha():
        Address.delete(0, END)
        City.delete(0, END)
        State.delete(0, END)
        messagebox.showerror("Validation Error", "Enter correct Address")
        return None

    if len(PhNo.get()) != 10 or not (PhNo.get().isdigit()):
        PhNo.delete(0, END)
        messagebox.showerror("Validation Error", "Enter correct Phone Number")
        return None

    cursor.execute("SELECT EXISTS(SELECT Ssn FROM BORROWER WHERE BORROWER.ssn = '" + new_ssn + "')")
    result = cursor.fetchall()
    if result == [(0,)]:
        address = ', '.join([Address.get(), City.get(), State.get()])
        bname = ' '.join([Fname.get(), Lname.get()])
        cursor.execute(
            "Insert into BORROWER (Card_ID, ssn,bname, address, phone) Values ('" + new_card_no + "', '" +
            new_ssn + "', '" + str(bname) + "', '" + address + "', '" + str(PhNo.get()) + "')")
        conn.commit()
        generate_message("Added Borrower")
    else:
        generate_message("Error, Borrower Already Exists!")


# end of Add Borrower


# Update Fines
def update_fine():
    cursor = conn.cursor()
    cursor.execute("SELECT BOOK_LOANS.Loan_Id, BOOK_LOANS.Date_in, BOOK_LOANS.Due_date FROM BOOK_LOANS")
    result = cursor.fetchall()
    for record in result:
        date_in = record[1]
        date_due = record[2]
        if date_in is None:
            date_in = today
        diff = (date_in - date_due)
        if diff.days > 0:
            fine = int(diff.days) * 0.25
        else:
            fine = 0
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE FINES SET FINES.fine_amt = '" + str(fine) + "' WHERE FINES.Loan_Id = '" + str(record[0]) + "'")
        conn.commit()
    generate_message("Fines Updated")


# End of Fines Update


# Show Fines
class show_fines(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.bookForCheckInID = None
        self.search_string = None
        self.data = None

        searchLabel = ttk.Label(self, text="Search here: Borrower ID")
        searchLabel.grid(row=0, column=0, padx=20, pady=20)
        search_text = ttk.Entry(self)
        search_text.grid(row=1, column=0)
        self.search_string = search_text.get()
        searchBtn = ttk.Button(self, text="Search", command=lambda: self.show_fines_bid(search_text.get()))
        searchBtn.grid(row=2, column=0)
        self.table = Treeview(self, columns=["ISBN", "TITLE", "Fine_Amt", "Date_In", "Status"])
        self.table.grid(row=3, column=0)
        self.table.heading('#0', text="ISBN")
        self.table.heading('#1', text="TITLE")
        self.table.heading('#2', text="Fine Amount")
        self.table.heading('#3', text="Date_In")
        self.table.heading('#4', text="Status")

        BackButton = ttk.Button(self, text="Back To HomePage", width=40,
                                command=lambda: controller.show_frame(HomePage))
        BackButton.grid(row=30, column=0)
        BackButton.grid_rowconfigure(5, weight=1)

    def show_fines_bid(self, search_s):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BOOK_LOANS.Isbn,BOOK.Title,FINES.fine_amt,BOOK_LOANS.date_in,case when fines.paid=1 then 'Paid' "
            "else 'Not Paid' END as fine_status FROM BOOK_LOANS join BOOK ON BOOK.Isbn = BOOK_LOANS.Isbn join FINES "
            "ON FINES.LOAN_ID = BOOK_LOANS.LOAN_ID where book_loans.Card_id = '" + search_s + "'")

        self.data = cursor.fetchall()
        for row in self.data:
            print(row)
        self.view_data()

    def view_data(self):
        self.table.delete(*self.table.get_children())
        for elem in self.data:
            self.table.insert('', 'end', text=str(elem[0]), values=(elem[1], elem[2], elem[3], elem[4]))
# end Fines
