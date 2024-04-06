from datetime import datetime
import tkinter as tk
from tkinter import Button, Checkbutton, Label, StringVar, Toplevel, ttk, messagebox
from tkinter import scrolledtext
from PIL import Image,ImageTk
import mysql.connector
import random
from chatbot import ChatBotApp
import speech_recognition as sr
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1550x800+0+0")

        self.bg = ImageTk.PhotoImage(file="D:/Chatbot/real/login.jpg")
        lbl_bg = tk.Label(self.root, image=self.bg)
        lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)

        frame = tk.Frame(self.root, bg="snow")
        frame.place(x=470, y=100, width=340, height=450)

        img1 = Image.open("D:/Chatbot/real/login1.png")
        img1 = img1.resize((100, 100))
        self.Photoimage1 = ImageTk.PhotoImage(img1)
        lblimg1 = tk.Label(image=self.Photoimage1, bg="snow", borderwidth=0)
        lblimg1.place(x=590, y=110, width=100, height=100)

        get_str = tk.Label(frame, text="PRIMROSE", font=("didot", 20, "bold"), fg="darkgreen", bg="snow")
        get_str.place(x=100, y=120)

        username = tk.Label(frame, text="E-mail", font=("didot", 15), fg="black", bg="snow")
        username.place(x=30, y=170)

        self.txtuser = ttk.Entry(frame, font=("didot", 13))
        self.txtuser.place(x=30, y=200, width=270)

        password = tk.Label(frame, text="Password", font=("didot", 15), fg="black", bg="snow")
        password.place(x=30, y=235)
        
        fpbtn = tk.Button(frame, text="Forgot Password?", command=self.fp_window, font=("didot", 10, "bold"), borderwidth=0, fg="black", bg="snow", activeforeground="black", activebackground="snow")
        fpbtn.place(x=30, y=295)

        self.txtpass = ttk.Entry(frame, show="*", font=("didot", 13))
        self.txtpass.place(x=30, y=260, width=270)

        loginbtn = tk.Button(frame, command=self.login, text="Login", font=("didot", 15, "bold"), bd=3, relief=tk.RIDGE, fg="snow", bg="darkgreen", activeforeground="snow", activebackground="darkgreen")
        loginbtn.place(x=110, y=330, width=120, height=35)

        registerbtn = tk.Button(frame, text="Register", command=self.register_win, font=("didot", 12, "bold"), borderwidth=0, fg="snow", bg="black", activeforeground="snow", activebackground="black")
        registerbtn.place(x=110, y=390, width=120)

    def register_win(self):
        self.register_window = tk.Toplevel(self.root)
        self.app = Register(self.register_window)

    def login(self):
        email = self.txtuser.get()
        password = self.txtpass.get()

        if email.strip() == "" or password.strip() == "":
            messagebox.showerror("Error", "All fields are required")
        else:
            if email == "admin" and password == "admin":
                messagebox.showinfo("Success", "Admin login successful!")
                self.root.destroy()
                launch_chatbot()  # Launch the chatbot GUI window
            else:
                if authenticate(email, password):
                    messagebox.showinfo("Success", "Login Successful!")
                    self.root.destroy()
                    self.launch_chatbot()  # Redirect to chatbot window after login
                else:
                    messagebox.showerror("Error", "Invalid email or password")

    def launch_chatbot(self):
        chatbot_app = ChatBotApp()
        chatbot_app.launch_chatbot()
    
    def resetpass(self):
        if self.txt_newpass.get() == "":
            messagebox.showerror("Error", "Please enter a new password")
        else:
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="motu", database="chatbot", auth_plugin='mysql_native_password')
                my_cursor = conn.cursor()
                queryy = "select * from user where email = %s"
                my_cursor.execute(queryy, (self.txtuser.get(),))
                row = my_cursor.fetchone()
                if row is None:
                    messagebox.showerror("Error", "Please provide a valid email")
                else:
                    queryyy = "update user set password=%s where email=%s"
                    value = (self.txt_newpass.get(), self.txtuser.get())
                    my_cursor.execute(queryyy, value)
                    conn.commit()  # Commit the changes to the database
                    messagebox.showinfo("Success", "Password reset successful!")
                    conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def fp_window(self):
        if self.txtuser.get() == "":
            messagebox.showerror("Error", "Please enter your Email to reset the password")
        else:
            conn = mysql.connector.connect(host="localhost", user="root", password="motu", database="chatbot", auth_plugin='mysql_native_password')
            my_cursor = conn.cursor()
            query = "select * from user where email=%s"
            value = (self.txtuser.get(),)
            my_cursor.execute(query, value)
            row = my_cursor.fetchone()
            if row is None:
                messagebox.showerror("Error", "Please enter a valid Email")
            else:
                conn.close()
                self.root2 = tk.Toplevel()
                self.root2.title("Forgot Password")
                self.root2.geometry("340x450+610+170")  # Fixed geometry specification

                l = Label(self.root2, text="Forgot Password", font=("didot", 20, "bold"), borderwidth=0, fg="green", bg="snow")
                l.place(x=0, y=10, relwidth=1)

                newpass = Label(self.root2, text="New Password", font=("didot", 15), borderwidth=0, fg="black", bg="snow")
                newpass.place(x=50, y=160)

                self.txt_newpass = ttk.Entry(self.root2, font=("didot", 13, "bold"))
                self.txt_newpass.place(x=50, y=200, width=250)

                btn = Button(self.root2, text="Reset", font=("didot", 13, "bold"), fg="snow", bg="black", command=self.resetpass)
                btn.place(x=150, y=250)

class ChatBotApp:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.intents = json.loads(open('intents.json').read())
        self.words = pickle.load(open('words.pkl', 'rb'))
        self.classes = pickle.load(open('classes.pkl', 'rb'))
        self.model = tf.keras.models.load_model('chatbot_model.h5')
        self.chat_history_file = 'chat_history.txt'
        self.init_ui()
    
    def clear_chat_history(self):
        with open(self.chat_history_file, 'w') as file:
            file.write("")  # Clear chat history file
        self.text_box.configure(state='normal')  # Enable editing of the text box
        self.text_box.delete(1.0, tk.END)  # Delete all content from the text box
        self.text_box.configure(state='disabled')  # Disable editing of the text box again

    def retrieve_chat_history(self):
        with open(self.chat_history_file, 'r') as file:
            chat_history = file.readlines()
        return chat_history

    def init_ui(self):
        self.root = tk.Tk()
        self.root.title("ChatBot")
        self.root.configure(bg="#E6F3FF")

        # Add comforting messages as a heading
        comforting_messages = [
            "You're not alone. I'm here to listen.",
            "It's okay not to be okay.",
            "You're stronger than you think.",
            "Take a deep breath. Everything will be okay.",
            "You're loved and valued."
        ]
        random_comforting_message = random.choice(comforting_messages)
        comforting_message_heading = tk.Label(self.root, text=random_comforting_message, font=('Arial', 16, 'bold'), bg="#E6F3FF", padx=10, pady=10)
        comforting_message_heading.pack()

        # Create and configure text box for messages
        self.text_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', font=('Arial', 12))
        self.text_box.pack(expand=True, fill='both', padx=10, pady=10)

        # Create entry box for typing messages
        self.entry_box = ttk.Entry(self.root, width=60, font=('Arial', 14))
        self.entry_box.pack(side=tk.LEFT,pady=10, padx=10)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.root, bg="#E6F3FF")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Make the frame expand horizontally

        send_button = ttk.Button(button_frame, text="Send", command=self.process_input, width=20)
        send_button.pack(side=tk.LEFT, padx=10, pady=10)  # Adjust the side of the button

        listen_button = ttk.Button(button_frame, text="Listen", command=self.listen_and_send, width=20)
        listen_button.pack(side=tk.LEFT, padx=10, pady=10)  # Adjust the side of the button

        clear_button = ttk.Button(button_frame, text="Clear Chat History", command=self.clear_chat_history, width=20)
        clear_button.pack(side=tk.LEFT, padx=10, pady=10)  # Adjust the side of the button

        logout_button = ttk.Button(button_frame, text="Logout", command=self.logout, width=20)
        logout_button.pack(side=tk.LEFT, padx=10, pady=10)  # Adjust the side of the button

        # Retrieve chat history and display it
        chat_history = self.retrieve_chat_history()
        for message in chat_history:
            self.text_box.insert(tk.END, message)

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0]*len(self.words)
        for w in sentence_words:
            for i, word in enumerate(self.words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)

    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def get_response(self, intents_list, intents_json):
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        return result

    def send_message(self, sender="user", message=None):
        if message is not None and message.strip() != "":
            if sender == "user":
                user_message = f"You: {message}\n"
                self.text_box.configure(state='normal')
                self.text_box.insert(tk.END, user_message, 'user_message')
                self.entry_box.delete(0, tk.END)  # Clear entry box
                bot_response = self.get_bot_response(message)
                self.send_message("bot", bot_response)  # Specify sender as "bot"
            else:
                bot_response = f"Bot: {message}\n"
                self.text_box.insert(tk.END, bot_response, 'bot_response')

            self.text_box.see(tk.END)
            self.store_message(sender, message)  # Store the message in chat history

    def process_input(self):
        message = self.entry_box.get()
        if message.strip() != "":
            self.send_message("user", message)

    def listen_and_send(self):
        query = self.listen()
        if query is not None:
            self.send_message("user", query)

    def get_bot_response(self, message):
        ints = self.predict_class(message)
        res = self.get_response(ints, self.intents)
        return res

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            audio = r.listen(source, timeout=5)  # Set a timeout of 5 seconds
        try:
            print("Recognizing...")
            query = r.recognize_google(audio)
            print(f"User: {query}")
            self.send_message("bot", query)  # Send recognized speech as a bot message
            return query
        except sr.WaitTimeoutError:
            print("Listening timed out")
        except Exception as e:
            print(e)
            print("Couldn't recognize the audio")

    def launch_chatbot(self):
        self.root.mainloop()
    
    def logout(self):
        self.root.destroy()  # Close the chatbot window
        print("Logged out successfully!")

    def store_message(self, sender, message):
        with open(self.chat_history_file, 'a') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"{timestamp} [{sender}]: {message}\n")

    def retrieve_chat_history(self):
        with open(self.chat_history_file, 'r') as file:
            chat_history = file.readlines()
        return chat_history
        
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
                    my_cursor.execute("INSERT INTO user (user_id, fname, lname, email, password, cpassword) VALUES (%s, %s, %s, %s, %s, %s)", (
                        self.var_userid.get(), self.var_firstname.get(), self.var_lastname.get(), self.var_email.get(), self.var_pass.get(), self.var_cpass.get()))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Registration", "Registration is successfully completed",parent=self.root)
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error: {e}")
    def return_login(self):
        self.root.destroy()
        
                
def authenticate(email, password):
    try:
        conn = mysql.connector.connect(host="localhost", username="root", password="motu", database="chatbot")
        cursor = conn.cursor()
        query = "select * from user where email=%s and password=%s"
        cursor.execute(query, (email, password))
        row = cursor.fetchone()
        conn.close()
        if row != None:
            return True
        else:
            return False
    except Exception as ex:
        messagebox.showerror("Error", f"Error due to: {str(ex)}")

def launch_chatbot():
    pass

def main():
    root = tk.Tk()
    obj = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
