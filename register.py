import tkinter as tk
from tkinter import Button, Checkbutton, StringVar, ttk, messagebox
from PIL import ImageTk
import mysql.connector
import random
from login import LoginWindow

class Register:
    def __init__(self, root):
        self.root = root
        self.root.title("Register")
        self.root.geometry("1600x900+0+0")

        # Variables
        self.var_userid = StringVar()
        x = random.randint(1, 999)
        self.var_userid.set(str(x))

        self.var_firstname = tk.StringVar()
        self.var_lastname = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_pass = tk.StringVar()
        self.var_cpass = tk.StringVar()
        self.var_check = tk.BooleanVar()

        # Background image
        self.bg = ImageTk.PhotoImage(file=r"D:\Chatbot\real\login.jpg")
        lbl_bg = tk.Label(self.root, image=self.bg)
        lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)

        # Main Frame
        frame = tk.Frame(self.root, bg="snow")
        frame.place(x=250, y=50, width=800, height=550)

        register_lbl = tk.Label(frame, text="PRIMROSE", font=("didot", 20, "bold"), fg="darkgreen", bg="snow")
        register_lbl.place(x=320, y=20)

        # Label and Entry
        # Row 1
        userid = tk.Label(frame, text="User ID", font=("didot", 15), bg="snow")
        userid.place(x=120, y=100)

        userid_entry = ttk.Entry(frame, textvariable=self.var_userid, font=("didot", 13))
        userid_entry.place(x=120, y=130, width=250)

        firstname = tk.Label(frame, text="First Name", font=("didot", 15), bg="snow", fg="black")
        firstname.place(x=420, y=100)

        self.txt_firstname = ttk.Entry(frame, textvariable=self.var_firstname, font=("didot", 13))
        self.txt_firstname.place(x=420, y=130, width=250)

        # Row 2
        lastname = tk.Label(frame, text="Last Name", font=("didot", 15), bg="snow", fg="black")
        lastname.place(x=120, y=170)

        self.txt_lastname = ttk.Entry(frame, textvariable=self.var_lastname, font=("didot", 13))
        self.txt_lastname.place(x=120, y=200, width=250)

        email = tk.Label(frame, text="E-mail", font=("didot", 15), bg="snow", fg="black")
        email.place(x=420, y=170)

        self.txt_email = ttk.Entry(frame, textvariable=self.var_email, font=("didot", 13))
        self.txt_email.place(x=420, y=200, width=250)

        # Row 3
        password = tk.Label(frame, text="Password", font=("didot", 15), bg="snow", fg="black")
        password.place(x=120, y=240)

        self.txt_password = ttk.Entry(frame, textvariable=self.var_pass, font=("didot", 13))
        self.txt_password.place(x=120, y=270, width=250)

        cpassword = tk.Label(frame, text="Confirm Password", font=("didot", 15), bg="snow", fg="black")
        cpassword.place(x=420, y=240)

        self.txtcpass = ttk.Entry(frame, textvariable=self.var_cpass, font=("didot", 13))
        self.txtcpass.place(x=420, y=270, width=250)

        # Check button
        Checkbtn = Checkbutton(frame, variable=self.var_check, text="I Agree To The Terms and Conditions",font=("didot", 13, "bold"), bg="snow", fg="black", onvalue=True, offvalue=False)
        Checkbtn.place(x=116, y=390)

         # Register Button
        registerbtn = Button(frame, command=self.register_data, text="Register", font=("didot", 14, "bold"),borderwidth=0, fg="snow", bg="darkgreen", activeforeground="snow", activebackground="darkgreen")
        registerbtn.place(x=230, y=450, width=120)

        # Login button
        registerbtn = Button(frame, command=self.return_login, text="Login", font=("didot", 14, "bold"),borderwidth=0, fg="snow", bg="black", activeforeground="snow", activebackground="black")
        registerbtn.place(x=430, y=450, width=120)

    def register_data(self):
        if self.var_firstname.get() == "" or self.var_lastname.get() == "" or self.var_email.get() == "":
            messagebox.showerror("Error", "All fields are required",parent=self.root)
        elif self.var_pass.get() != self.var_cpass.get():
            messagebox.showerror("Error", "Enter the correct password",parent=self.root)
        elif not self.var_check.get():
            messagebox.showerror("Error", "Agree to our terms and conditions",parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="motu",
                    database="chatbot",
                    auth_plugin='mysql_native_password'
                )
                my_cursor = conn.cursor()
                query = "SELECT * FROM user WHERE email = %s"
                value = (self.var_email.get(),)
                my_cursor.execute(query, value)
                rows = my_cursor.fetchone()
                if rows is not None:
                    messagebox.showerror("Error", "User already exists, please enter another E-mail",parent=self.root)
                else:
                    my_cursor.execute("INSERT INTO user (userUid, fname, lname, email, password, cpassword) VALUES (%s, %s, %s, %s, %s, %s)", (
                        self.var_userid.get(), self.var_firstname.get(), self.var_lastname.get(), self.var_email.get(), self.var_pass.get(), self.var_cpass.get()))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Registration", "Registration is successfully completed",parent=self.root)
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error: {e}")
    
    def return_login(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Register(root)
    root.mainloop()
