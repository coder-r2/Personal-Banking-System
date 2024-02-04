import mysql.connector as sqltor
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk, END
from PIL import Image, ImageTk
import datetime
import string
import os

# Constants
SMALL_WINDOW_DIM = (400, 250)
LARGE_WINDOW_DIM = (950, 600)
COLOR1 = '#2A2F4F'
COLOR2 = '#917FB3'
COLOR3 = '#E5BEEC'
COLOR4 = '#FDE2F3'
GRAY = '#BDBDBD'
FONT10 = ('Roboto', 10)
FONT12 = ('Roboto', 12)
FONT15 = ('Roboto', 15)
FONT20 = ('Roboto', 20)
BFONT = ('Helvetica', 30)
MYSQL_CONNECTION_ESTABLISHED = True
CURRENT_ACCNO = None
GENDERS = ['Male', 'Female', 'Other']
UP = u'\u25B4'
DOWN = u'\u25BE'
 
# Images
eye_open = Image.open('assets/eye_open.png').resize((13, 13))
eye_close = Image.open('assets/eye_close.png').resize((13, 13))
logout = Image.open('assets/logout.png')
withdraw = Image.open('assets/withdraw.png')
deposit = Image.open('assets/deposit.png')
transfer = Image.open('assets/transfer.png')
history = Image.open('assets/history.png')
info = Image.open('assets/info.png')
search = Image.open('assets/search.png')

# MySQL Functions
def mysql_init():
    cur.execute('CREATE DATABASE IF NOT EXISTS BANKDB')
    cur.execute('USE BANKDB')
    create_cdtable_command = '''CREATE TABLE IF NOT EXISTS CUST_DETAILS(\
        AccNo int(5) PRIMARY KEY AUTO_INCREMENT, \
        Name varchar(25), DOB date, Gender varchar(6), \
        Phone_Number varchar(10), Address varchar(50), \
        Email varchar(25), Password varchar(15), \
        Encryption_Key int(1), \
        Time_of_Creation datetime, Current_Bal int default 0) AUTO_INCREMENT=10000'''
    cur.execute(create_cdtable_command)
    cnx.commit()
    cur.execute('ALTER TABLE CUST_DETAILS AUTO_INCREMENT=10001')
    cnx.commit()

    if not os.path.exists('Receipts'):
        os.makedirs('Receipts')

def mysql_get(table:str, column_string):
    cur.execute(f'select {column_string} from {table}')
    data = cur.fetchall()
    return data

# Tkinter Formatting
def format_window(win:tk.Tk, size:tuple, title:str, background_color:str=COLOR1):
    win.geometry(f'{size[0]}x{size[1]}')
    win.title(title)
    win['bg'] = background_color
    win.bind('<Escape>', lambda _: win.destroy())

def format_button(button:tk.Button, hover_color, unhover_color):
    button.bind('<Leave>', lambda _: button.configure(bg=unhover_color))
    button.bind('<Enter>', lambda _: button.configure(bg=hover_color))

# Windows

def mysql_connect():
    def close():
        dbms_connect_win.destroy()
        mysql_init()
        
    dbms_connect_win = tk.Tk()
    format_window(dbms_connect_win, SMALL_WINDOW_DIM, 'MySQL Connect Window')

    tk.Label(dbms_connect_win, text='MySQL Login Details', font=FONT20, background=COLOR1, foreground=COLOR4).pack(pady=20)

    uname_entry = tk.Entry(dbms_connect_win, font=FONT15, width=15)
    attach_placeholder(uname_entry, 'MYSQL Username')
    uname_entry.pack(pady=5)
    
    pass_entry = tk.Entry(dbms_connect_win, font=FONT15, width=15, show='*')
    attach_placeholder(pass_entry, 'MYSQL Password', True)
    pass_entry.pack(pady=5)
    
    auth_button = tk.Button(dbms_connect_win, fg=COLOR1, text='Connect to Database', font=FONT15, command=lambda: validate_input(mysql_authenticate, close, login, uname_entry, pass_entry))
    format_button(auth_button, COLOR4, COLOR3)
    auth_button.pack(pady=25)
    
    pass_entry.focus_set()
    dbms_connect_win.bind('<Return>', lambda e: validate_input(mysql_authenticate, close, login, uname_entry, pass_entry))
    dbms_connect_win.mainloop()

def login():
    def close():
        login_win.destroy()
    
    def to_signup():
        login_win.destroy()
        signup()
        
    login_win = tk.Tk()
    format_window(login_win, LARGE_WINDOW_DIM, 'Login Window')
    
    panel = tk.Frame(login_win, bg=COLOR3, height=400, width=300)
    tk.Label(panel, text='Login', font=FONT20, bg=COLOR3, fg=COLOR1).pack(pady=10)
    panel.pack(expand=True, fill='both', padx=300, pady=100)
    
    mid_frame = tk.Frame(panel, bg=COLOR3)
    mid_frame.pack(pady=45)
    
    accno_entry = tk.Entry(mid_frame, font=FONT15, width=20)
    accno_entry.pack(pady=10)
    
    pass_entry = tk.Entry(mid_frame, font=FONT15, width=20, show='*')
    pass_entry.pack(pady=10)
    
    auth_button = tk.Button(panel, fg=COLOR1, text='Login', font=FONT15, command=lambda: validate_input(validate_login_info, close, main_menu, accno_entry, pass_entry))
    auth_button.pack(side='bottom', pady=25)
    
    back_to_signup = tk.Button(panel, fg=COLOR4, text='Signup Instead', font=FONT15, bg=COLOR1, command=to_signup)
    back_to_signup.pack(side='bottom', pady=15)
    
    attach_placeholder(accno_entry, 'Account Number')
    attach_placeholder(pass_entry, 'Password', True)
    format_button(auth_button, COLOR4, COLOR3)
    
    pass_entry.focus_set()
    login_win.mainloop()

def signup():
    def close():
        global CURRENT_ACCNO
        password = pass_entry.get()
        phno = ph_entry.get()
        last_dig = int(phno[-1])
        encoded_password = encode(password, last_dig)
        data = (
            name_entry.get(), 
            f'{year_var.get()}-{month_var.get()}-{date_var.get()}',
            gender_var.get(),
            phno,
            add_entry.get('1.0', 'end-1c'),
            email_entry.get(),
            encoded_password,
            last_dig,
            str(datetime.datetime.now())[:-7]
            )
        cmd = f'''insert into CUST_DETAILS(\
            Name, DOB, Gender, Phone_Number, Address, Email, \
            Password, Encryption_Key, Time_of_Creation) values{data}'''
        cur.execute(cmd)
        cnx.commit()
        acno = mysql_get('CUST_DETAILS', 'AccNo')[-1][0]
        cmd = f'''CREATE TABLE TRANSAC{acno}(\
            TransactionID int(3) PRIMARY KEY AUTO_INCREMENT, \
            Sender int(5) REFERENCES cust_details(AccNo), \
            Receiver int(5) REFERENCES cust_details(AccNo), \
            Amount int(6) NOT NULL, \
            TransactionTime datetime) AUTO_INCREMENT=100'''
        cur.execute(cmd)
        cnx.commit()
        msg.showinfo('Account Created', f'Your account number is\n {acno}')
        CURRENT_ACCNO = acno
        signup_win.destroy()
    
    def to_login():
        signup_win.destroy()
        login()
    
    signup_win = tk.Tk()
    
    eye_open_image = ImageTk.PhotoImage(eye_open)
    eye_close_image = ImageTk.PhotoImage(eye_close)
    
    panel = tk.Frame(signup_win, width=800, height=500, bg=COLOR3)
    tk.Label(panel, text='Signup', font=FONT20, bg=COLOR3, fg=COLOR1).pack(pady=10)
    lsr_frame = tk.Frame(panel, bg=COLOR3)
    lsr_frame.pack(pady=5)
    panel.pack(expand=True, fill='both', padx=50, pady=50)
    
    left_frame = tk.Frame(lsr_frame, bg=COLOR3)
    name_frame = tk.Frame(left_frame, bg=COLOR3)
    name_frame.pack(pady=5)
    dob_frame = tk.Frame(left_frame, bg=COLOR3)
    dob_frame.pack(pady=5)
    gender_frame = tk.Frame(left_frame, bg=COLOR3)
    gender_frame.pack(pady=5)
    ph_no_frame = tk.Frame(left_frame, bg=COLOR3)
    ph_no_frame.pack(pady=5)
    address_frame = tk.Frame(left_frame, bg=COLOR3)
    address_frame.pack(pady=5)
    left_frame.pack(side='left', expand=True, fill='both', padx=5, pady=5)
    
    ttk.Separator(lsr_frame, orient='vertical').pack(side='left', fill='y')
    
    right_frame = tk.Frame(lsr_frame, bg=COLOR3)
    email_frame = tk.Frame(right_frame, bg=COLOR3)
    email_frame.pack(pady=5)
    pass_frame = tk.Frame(right_frame, bg=COLOR3)
    pass_frame.pack(pady=5)
    passcon_frame = tk.Frame(right_frame, bg=COLOR3)
    passcon_frame.pack(pady=5)
    right_frame.pack(side='left', expand=True, fill='both', padx=5, pady=5)
    
    signup_button = tk.Button(panel, fg=COLOR4, text='Signup', font=FONT15, bg=COLOR1, command=lambda: validate_input(validate_signup_info, close, main_menu, email_entry, pass_entry, passcon_entry))
    signup_button.pack(pady=20)
    
    back_to_login = tk.Button(panel, fg=COLOR4, text='Login Instead', font=FONT15, bg=COLOR1, command=to_login)
    back_to_login.pack(pady=20)
    
    tk.Label(name_frame, text='Enter your name:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    name_entry = tk.Entry(name_frame, font=FONT12, width=20)
    name_entry.pack(side='left', padx=5)
    
    year_var = tk.StringVar()
    month_var = tk.StringVar()
    date_var = tk.StringVar()
    tk.Label(dob_frame, text='Enter your DOB:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    year_spin = ttk.Combobox(dob_frame, width=5, font=FONT12, values=[i for i in range(1950, 2008)], textvariable=year_var)
    year_spin.pack(side='left', padx=5)
    month_spin = ttk.Combobox(dob_frame, width=3, font=FONT12, values=[i for i in range(1, 13)], textvariable=month_var)
    month_spin.pack(side='left', padx=5)
    date_spin = ttk.Combobox(dob_frame, width=3, font=FONT12, values=[i for i in range(1, 32)], textvariable=date_var)
    date_spin.pack(side='left', padx=5)
    
    gender_var = tk.StringVar(value=GENDERS[2])
    tk.Label(gender_frame, text='Gender:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    male_button = ttk.Radiobutton(gender_frame, text=GENDERS[0], variable=gender_var, value=GENDERS[0])
    male_button.pack(side='left', padx=5)
    female_button = ttk.Radiobutton(gender_frame, text=GENDERS[1], variable=gender_var, value=GENDERS[1])
    female_button.pack(side='left', padx=5)
    other_button = ttk.Radiobutton(gender_frame, text=GENDERS[2], variable=gender_var, value=GENDERS[2])
    other_button.pack(side='left', padx=5)
    
    tk.Label(ph_no_frame, text='Enter Phone Number:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    ph_entry = tk.Entry(ph_no_frame, font=FONT12, width=20)
    ph_entry.pack(side='left', padx=5)
    
    tk.Label(address_frame, text='Enter Address:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    add_entry = tk.Text(address_frame, width=25, height=3, font=FONT12)
    add_entry.pack(side='left', padx=5)
    
    tk.Label(email_frame, text='Enter Email:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    email_entry = tk.Entry(email_frame, font=FONT12, width=20)
    email_entry.pack(side='left', padx=5)
    
    tk.Label(pass_frame, text='Enter Password:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    pass_entry = tk.Entry(pass_frame, font=FONT12, width=20)
    pass_entry.pack(side='left', padx=5)
    eye_button1 = tk.Button(pass_frame, image=eye_open_image, font=FONT10, bg=COLOR2, fg=COLOR1)
    eye_button1.pack(padx=5)
    
    tk.Label(passcon_frame, text='Confirm Password:', font=FONT15, bg=COLOR3, fg=COLOR1, justify='right').pack(side='left', padx=5)
    passcon_entry = tk.Entry(passcon_frame, font=FONT12, width=20)
    passcon_entry.pack(side='left', padx=5)
    eye_button2 = tk.Button(passcon_frame, image=eye_open_image, font=FONT10, bg=COLOR2, fg=COLOR1)
    eye_button2.pack(padx=5)
    
    warning_label = tk.Label(right_frame, fg='red', bg=COLOR3, font=FONT10)
    warning_label.pack(pady=15)
    
    format_window(signup_win, LARGE_WINDOW_DIM, 'Signup Window')
    attach_placeholder(name_entry, 'Full Name')
    attach_placeholder(ph_entry, 'Valid Number (10 Digits)')
    attach_placeholder(email_entry, 'Valid Email')
    attach_placeholder(pass_entry, 'Password', True)
    attach_placeholder(passcon_entry, 'Password', True)
    format_button(signup_button, COLOR2, COLOR1)
    show_entry_button(eye_button1, pass_entry, eye_close_image, eye_open_image)
    show_entry_button(eye_button2, passcon_entry, eye_close_image, eye_open_image)
    
    signup_win.mainloop()

def main_menu():
    def close():
        if msg.askyesno('Confirmation', 'Do you really want to logout?'):
            main_menu.destroy()
            login()
    
    def info_frame_func():
        nonlocal a
        a.pack_forget()
        a = info_frame
        cbal_label.configure(text=f"Current Balance :  {mysql_get(f'cust_details where AccNo={CURRENT_ACCNO}', 'Current_Bal')[0][0]}")
        a.pack(padx=15, pady=15)
    
    def withdraw_frame_func():
        nonlocal a
        a.pack_forget()
        a = withdraw_frame
        a.pack(padx=15, pady=15)
        
    def deposit_frame_func():
        nonlocal a
        a.pack_forget()
        a = deposit_frame
        a.pack(padx=15, pady=15)
    
    def transfer_frame_func():
        nonlocal a
        a.pack_forget()
        a = transfer_frame
        a.pack(padx=15, pady=15)
    
    def history_frame_func():
        nonlocal a
        a.pack_forget()
        a = history_frame
        a.pack(padx=15, pady=15)
        if disp['state']=='disabled':
            disp.configure(state='active')
        disp.delete('1.0', END)
        disp.insert(END, '================================================================\n')
        disp.insert(END, 'Transaction ID\t\tTime\t\t\tTransaction Type\t\t\tAmount\n')
        disp.insert(END, '================================================================\n')
        trecs = mysql_get(f'transac{CURRENT_ACCNO}', '*')
        for trec in trecs:
            if not trec[1]:
                ttype = 'Deposit'
                char = UP
            elif not trec[2]:
                ttype = 'Withdrawal'
                char = DOWN
            elif trec[1]==int(CURRENT_ACCNO):
                ttype = f'Transfer to {trec[2]}'
                char = DOWN
            elif trec[2]==int(CURRENT_ACCNO):
                ttype = f'Transfer from {trec[1]}'
                char = UP
            disp.insert(END, f'{CURRENT_ACCNO}{ttype[0]}{trec[0]}\t\t{trec[4]}\t\t\t{ttype}\t\t\t{char}{trec[3]}\n')
        if disp['state']=='active':
            disp.configure(state='disabled')
    
    def withdraw_func():
        try:
            amt = int(withdraw_entry.get())
            cbal = mysql_get(f'cust_details where AccNo={CURRENT_ACCNO}', 'Current_Bal')[0][0]
            if amt >= cbal:
                raise Exception
        except ValueError:
            msg.showerror('Error', 'Enter appropriate value.')
            return
        except:
            msg.showerror('Error', 'Account Balance Not Sufficient')
            return
        finally:
            withdraw_entry.delete(0, END)
            
        if msg.askyesno('Confirmation', f'Withdraw Rs. {amt}?'):
            cmd = f"insert into transac{CURRENT_ACCNO}(Sender, Amount, TransactionTime) values ({CURRENT_ACCNO},{amt} , '{str(datetime.datetime.now())[:-7]}')"
            cur.execute(cmd)
            cnx.commit()
            trec = mysql_get(f'transac{CURRENT_ACCNO}', '*')[-1]
            cmd = f'update cust_details set Current_Bal = Current_Bal-{amt} where AccNo={CURRENT_ACCNO}'
            cur.execute(cmd)
            cnx.commit()
            rcptno = f'{CURRENT_ACCNO}W{trec[0]}'
            temp = open('assets\\withdraw_template.txt')
            con = temp.read()
            recpt = open('Receipts\\'+rcptno+'.txt', 'w')
            recpt.write(con.format(rcptno, CURRENT_ACCNO, str(amt)+' '*(6-len(str(amt))), str(trec[4])[:10], str(trec[4])[11:]))
            temp.close()
            recpt.close()
            os.startfile(f'Receipts\\{rcptno}.txt')
            info_frame_func()
    
    def deposit_func():
        try:
            amt = int(deposit_entry.get())
        except ValueError:
            msg.showerror('Error', 'Enter appropriate value.')
            return
        finally:
            deposit_entry.delete(0, END)
            
        if msg.askyesno('Confirmation', f'Deposit Rs. {amt}?'):
            cmd = f"insert into transac{CURRENT_ACCNO}(Receiver, Amount, TransactionTime) values ({CURRENT_ACCNO},{amt} , '{str(datetime.datetime.now())[:-7]}')"
            cur.execute(cmd)
            cnx.commit()
            trec = mysql_get(f'transac{CURRENT_ACCNO}', '*')[-1]
            cmd = f'update cust_details set Current_Bal = Current_Bal+{amt} where AccNo={CURRENT_ACCNO}'
            cur.execute(cmd)
            cnx.commit()
            rcptno = f'{CURRENT_ACCNO}D{trec[0]}'
            temp = open('assets\\deposit_template.txt')
            con = temp.read()
            recpt = open('Receipts\\'+rcptno+'.txt', 'w')
            recpt.write(con.format(rcptno, CURRENT_ACCNO, str(amt)+' '*(6-len(str(amt))), str(trec[4])[:10], str(trec[4])[11:]))
            temp.close()
            recpt.close()
            os.startfile(f'Receipts\\{rcptno}.txt')
            info_frame_func()
            
    def transfer_func():
        try:
            amt = int(transfer_entry.get())
            cbal = mysql_get(f'cust_details where AccNo={CURRENT_ACCNO}', 'Current_Bal')[0][0]
            if amt >= cbal:
                raise Exception
        except ValueError:
            msg.showerror('Error', 'Enter appropriate value.')
        except:
            msg.showerror('Error', 'Account Balance Not Sufficient')
            return
        finally:
            transfer_entry.delete(0, END)
            bfacno_entry.delete(0, END)
        
        if msg.askyesno('Confirmation', f'Transfer Rs.{amt} to {bfacno}'):
            t = str(datetime.datetime.now())[:-7]
            cmd = f"insert into transac{CURRENT_ACCNO}(Sender, Receiver, Amount, TransactionTime) values ({CURRENT_ACCNO}, {bfacno}, {amt}, '{t}')"
            cur.execute(cmd)
            cnx.commit()
            cmd = f"insert into transac{bfacno}(Sender, Receiver, Amount, TransactionTime) values ({CURRENT_ACCNO}, {bfacno}, {amt}, '{t}')"
            cur.execute(cmd)
            cnx.commit()
            trec = mysql_get(f'transac{CURRENT_ACCNO}', '*')[-1]
            cmd = f'update cust_details set Current_Bal = Current_Bal-{amt} where AccNo={CURRENT_ACCNO}'
            cur.execute(cmd)
            cmd = f'update cust_details set Current_Bal = Current_Bal+{amt} where AccNo={bfacno}'
            cur.execute(cmd)
            cnx.commit()
            
            rcptno = f'{CURRENT_ACCNO}W{trec[0]}'
            temp = open('assets\\transfer_template.txt')
            con = temp.read()
            recpt = open('Receipts\\'+rcptno+'.txt', 'w')
            recpt.write(con.format(rcptno, CURRENT_ACCNO, bfacno, str(amt)+' '*(6-len(str(amt))), str(trec[4])[:10], str(trec[4])[11:]))
            temp.close()
            recpt.close()
            os.startfile(f'Receipts\\{rcptno}.txt')
            info_frame_func()
    
    def search_btn_func():
        nonlocal bfacno
        try:
            bfacno = int(bfacno_entry.get())
            acnos = [i[0] for i in mysql_get(f'cust_details where AccNo<>{CURRENT_ACCNO}', 'AccNo')]
            if bfacno not in acnos:
                raise Exception('Account Number not found.')
            if not msg.askyesno('Comfirmation', f'Account Holder : {mysql_get(f"cust_details where AccNo={bfacno}", "Name")[0][0]}'):
                raise Exception('No other accounts found.')
        except ValueError:
            msg.showerror('Error', 'Enter appropriate value.')
            return
        except Exception as e:
            msg.showerror('Error', e)
            return
                
    main_menu = tk.Tk()
    
    cur.execute(f'select * from cust_details where AccNo={CURRENT_ACCNO}')
    account_details = cur.fetchone()
    
    search_image = ImageTk.PhotoImage(search)
    logout_image = ImageTk.PhotoImage(logout)
    info_image = ImageTk.PhotoImage(info)
    withdraw_image = ImageTk.PhotoImage(withdraw)
    deposit_image = ImageTk.PhotoImage(deposit)
    history_image = ImageTk.PhotoImage(history)
    transfer_image = ImageTk.PhotoImage(transfer)
    
    main_frame = tk.Frame(main_menu, bg=COLOR3)
    
    welcome_frame = tk.Frame(main_frame, bg=COLOR3)
    tk.Label(welcome_frame, text='Welcome To\nR.R. Bank', font=BFONT, bg=COLOR3).pack()
    welcome_frame.pack(padx=15, pady=60)
    
    info_frame = tk.Frame(main_frame, bg=COLOR3)
    tk.Label(info_frame, text=f'Account Number  :  {account_details[0]}', font=FONT12, bg=COLOR3).pack(pady=10)
    tk.Label(info_frame, text=f'Account Holder  :  {account_details[1]}', font=FONT12, bg=COLOR3).pack(pady=10)
    tk.Label(info_frame, text=f'Phone Number    :  {account_details[4]}', font=FONT12, bg=COLOR3).pack(pady=10)
    tk.Label(info_frame, text=f'Email           :  {account_details[6]}', font=FONT12, bg=COLOR3).pack(pady=10)
    tk.Label(info_frame, text=f'Password        :  {decode(account_details[7], account_details[8])}', font=FONT12, bg=COLOR3).pack(pady=10)
    cbal_label = tk.Label(info_frame, text=f'Current Balance :  {account_details[10]}', font=FONT12, bg=COLOR3)
    cbal_label.pack(pady=10)
    
    withdraw_frame = tk.Frame(main_frame, bg=COLOR3)
    tk.Label(withdraw_frame, text='Withdraw', font=FONT20, bg=COLOR3).pack()
    f1 = tk.Frame(withdraw_frame, bg=COLOR3)
    tk.Label(f1, text='Enter Withdraw Amount: ', font=FONT12, bg=COLOR3).pack(side='left', padx=5, pady=10, fill='x')
    withdraw_entry = tk.Entry(f1, font=FONT15, width=15)
    withdraw_entry.pack(side='right', padx=5)
    f1.pack(pady=10)
    withdraw_btn = tk.Button(withdraw_frame, fg=COLOR4, text='Withdraw', font=FONT15, bg=COLOR1, command=withdraw_func)
    withdraw_btn.pack(pady=10)
    
    deposit_frame = tk.Frame(main_frame, bg=COLOR3)
    tk.Label(deposit_frame, text='Deposit', font=FONT20, bg=COLOR3).pack(padx=10)
    f2 = tk.Frame(deposit_frame, bg=COLOR3)
    tk.Label(f2, text='Enter Deposit Amount: ', font=FONT12, bg=COLOR3).pack(side='left', padx=5, pady=10, fill='x')
    deposit_entry = tk.Entry(f2, font=FONT15, width=15)
    deposit_entry.pack(side='right', padx=5)
    f2.pack(pady=10)
    deposit_btn = tk.Button(deposit_frame, fg=COLOR4, text='Deposit', font=FONT15, bg=COLOR1, command=deposit_func)
    deposit_btn.pack(pady=10)
    
    transfer_frame = tk.Frame(main_frame, bg=COLOR3)
    tk.Label(transfer_frame, text='Transfer', font=FONT20, bg=COLOR3).pack(padx=10)
    f3 = tk.Frame(transfer_frame, bg=COLOR3)
    tk.Label(f3, text='Enter Beneficiary Account Number: ', font=FONT12, bg=COLOR3).pack(side='left', padx=5, pady=10, fill='x')
    bfacno_entry = tk.Entry(f3, font=FONT15, width=15)
    bfacno_entry.pack(side='left', padx=5)
    search_button = tk.Button(f3, image=search_image, font=FONT10, bg=COLOR2, fg=COLOR3, command=search_btn_func)
    search_button.pack(side='left', padx=5)
    f3.pack(pady=10)
    f4 = tk.Frame(transfer_frame, bg=COLOR3)
    tk.Label(f4, text='Enter Transfer Amount: ', font=FONT12, bg=COLOR3).pack(side='left', padx=5, pady=10, fill='x')
    transfer_entry = tk.Entry(f4, font=FONT15, width=15)
    transfer_entry.pack(side='right', padx=5)
    f4.pack(pady=10)
    transfer_btn = tk.Button(transfer_frame, fg=COLOR4, text='Transfer', font=FONT15, bg=COLOR1, command=transfer_func)
    transfer_btn.pack(pady=10)
    bfacno = None
    
    history_frame = tk.Frame(main_frame, bg=COLOR3)
    tk.Label(history_frame, text='Transaction History', font=FONT20, bg=COLOR3).pack(padx=10)
    disp = tk.Text(history_frame, height=15, width=75, font=FONT15)
    disp.pack(pady=20)
    
    a = welcome_frame
    
    panel = tk.Frame(main_menu, width=900, height=150, bg=COLOR1)
    info_button = tk.Button(panel, bg=COLOR3, text='Account Info', font=FONT10, image=info_image, compound='top', command=info_frame_func)
    info_button.pack(side='left', padx=10, pady=10)
    withdraw_button = tk.Button(panel, bg=COLOR3, text='Withdraw', font=FONT10, image=withdraw_image, compound='top', command=withdraw_frame_func)
    withdraw_button.pack(side='left', padx=10, pady=10)
    deposit_button = tk.Button(panel, bg=COLOR3, text='Deposit', font=FONT10, image=deposit_image, compound='top', command=deposit_frame_func)
    deposit_button.pack(side='left', padx=10, pady=10)
    transfer_button = tk.Button(panel, bg=COLOR3, text='Transfer', font=FONT10, image=transfer_image, compound='top', command=transfer_frame_func)
    transfer_button.pack(side='left', padx=10, pady=10)
    history_button = tk.Button(panel, bg=COLOR3, text='History', font=FONT10, image=history_image, compound='top', command=history_frame_func)
    history_button.pack(side='left', padx=10, pady=10)
    panel.pack(fill='x', padx=5, pady=5)
    
    main_frame.pack(pady=20)
    
    logout_button = tk.Button(main_menu, image=logout_image, bg=COLOR3, command=close)
    logout_button.place(relx=0.95, rely=0.92)
    
    format_window(main_menu, LARGE_WINDOW_DIM, 'Main Menu', COLOR3)
    
    attach_placeholder(deposit_entry, 'Deposit Amt')
    attach_placeholder(bfacno_entry, 'Account Number')
    
    main_menu.mainloop()

def clean_exit():
    cur.close()
    cnx.close()

# Other Functions

def mysql_authenticate(uname:str, pword:str) -> bool:
    """Authenticates MySQL Connection"""
    global cnx
    global cur
    global MYSQL_CONNECTION_ESTABLISHED
    
    try:
        cnx = sqltor.connect(host='localhost', user=uname, password=pword, charset='utf8')
        cur = cnx.cursor()
    except sqltor.errors.ProgrammingError:
        msg.showerror('Error', 'Incorrect MySQL Details')
        return False
    else:
        msg.showinfo('Success', 'Connection Established!')
        MYSQL_CONNECTION_ESTABLISHED = True
        return True

def encode(string, shift):
    encoded = ''
    for i in string:
        encoded += chr(ord(i)+shift)
    return encoded

def decode(string, shift):
    decoded = ''
    for i in string:
        decoded += chr(ord(i)-shift)
    return decoded

def validate_input(validate_func, win_closer, next_win_func, *entry_boxes:tk.Entry, **other_args):
    entry_values = tuple([entry.get() for entry in entry_boxes])
    if validate_func(*entry_values, **other_args):
        win_closer()
        next_win_func()
    else:
        for entry in entry_boxes:
            entry.delete(0, END)
        entry_boxes[0].focus_set()
        msg.showerror('Error', 'Invalid Details')
        
def validate_signup_info(email:str, password:str, con_password:str):
    condition1 = (password==con_password)
    condition2 = (len(password) >= 10)
    condition3 = any((iter1 in string.punctuation) for iter1 in password) # Detects presence of Special Characters
    condition4 = any((iter2 in string.ascii_lowercase) for iter2 in password) # Detects presence of Lowercase Characters
    condition5 = any((iter3 in string.ascii_uppercase) for iter3 in password) # Detects presence of Uppercase Characters
    condition6 = any((iter4 in string.digits) for iter4 in password) # Detects presence of Digits
    condition7 = all((iter5 in email) for iter5 in '@.')
    error_msg = ''
    if not condition1:
        error_msg += 'Passwords do not match.'
    if not condition2:
        error_msg += '\nPassword must be atleast 10 characters long.'
    if not condition3:
        error_msg += '\nPassword must contain a special character.'
    if not condition4:
        error_msg += '\nPassword must contain a lowercase letter.'
    if not condition5:
        error_msg += '\nPassword must contain an uppercase letter.'
    if not condition6:
        error_msg += '\nPassword must contain a digit.'
    if not condition7:
        error_msg += '\nInvalid Email'
    
    if all([condition1, condition2, condition3, condition4, condition5, condition6, condition7]):
        return True
    else:
        msg.showerror('Weak Password', error_msg)
        return False
    
def validate_login_info(accno, password):
    global CURRENT_ACCNO
    data = [[row[0], decode(row[1], row[2])] for row in mysql_get('cust_details', 'AccNo, Password, Encryption_Key')]
    if [int(accno), password] in data:
        CURRENT_ACCNO = accno
        return True
    else:
        return False

def attach_placeholder(entry_box:tk.Entry, placeholder_text:str, password=False):
    def entry_selected(_):
        if entry_box.get() == placeholder_text and entry_box['fg']==GRAY:
            entry_box.delete(0, END)
            entry_box.configure(fg=i_color, font=i_font)
            if password:
                entry_box.configure(show='*')
    
    def entry_deselected(_):
        if not entry_box.get():
            entry_box.configure(fg=GRAY)
            entry_box.insert(0, placeholder_text)
            if password:
                entry_box.configure(show='')
    
    i_font = entry_box['font']
    i_color = entry_box['fg']

    entry_box.configure(fg=GRAY)
    entry_box.insert(0, placeholder_text)
    entry_box.bind('<FocusIn>', entry_selected)
    entry_box.bind('<FocusOut>', entry_deselected)    

def show_entry_button(button:tk.Button, entry:tk.Entry, img_sel, img_desel):
    def show(_):
        entry.configure(show='')
        button.configure(image=img_sel)
    def hide(_):
        entry.configure(show='*')
        button.configure(image=img_desel)
    button.bind('<ButtonPress>', show)
    button.bind('<ButtonRelease>', hide)
    
def run():
    mysql_connect()
    if MYSQL_CONNECTION_ESTABLISHED:
        clean_exit()

run()
