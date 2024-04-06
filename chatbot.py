import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
import speech_recognition as sr
import os
from datetime import datetime

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

# Instantiate the ChatBotApp class and launch the chatbot
if __name__ == "__main__":
    app = ChatBotApp()
    app.launch_chatbot()
