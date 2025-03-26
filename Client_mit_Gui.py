import socket
import threading
import base64
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Server Settings
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

font_size = 11

class ChatClient:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("250x125")  # Set size of the login window

        self.username = ""

        # Create login frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        # Username input
        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()

        # Login button
        self.login_button = tk.Button(self.login_frame, text="Login",command=self.connect_to_server)
        self.login_button.pack()

        # Create chat frame (initially hidden)
        self.chat_frame = tk.Frame(self.root)

        # Chat display area with font configuration
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, state='disabled', width=50, height=20, font=("Arial", font_size))
        self.chat_display.pack(pady=10)

        # Message entry field
        self.msg_entry = tk.Entry(self.chat_frame, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=10)
        self.msg_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Configure tags for different fonts
        self.chat_display.tag_configure("user", font=("Arial", font_size), foreground="green")
        self.chat_display.tag_configure("other", font=("Arial", font_size), foreground= "gray")
        self.chat_display.tag_configure("server", font=("Arial", font_size), foreground="orange")
        self.chat_display.tag_configure("private", font=("Arial", font_size), foreground="magenta")

        self.client_socket = None

    def connect_to_server(self):
        try:
            # Create a socket and connect to the server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.username = self.username_entry.get()
            if not self.username:
                messagebox.showerror("Error", "Username cannot be empty!")
                return

            # Send the username to the server
            self.client_socket.send(base64.b64encode(self.username.encode()))
            welcome_msg = base64.b64decode(self.client_socket.recv(1024)).decode()

            # Display the welcome message
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, welcome_msg + "\n", "server")
            self.chat_display.config(state='disabled')

            # Switch to the chat frame
            self.login_frame.pack_forget()
            self.chat_frame.pack()
            self.root.geometry("")  # Resize window automatically to fit chat

            # Start a thread to receive messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def receive_messages(self):
        while True:
            try:
                # Receive and decode messages from the server
                msg_encoded = self.client_socket.recv(1024)
                if not msg_encoded:
                    break
                msg_decoded = base64.b64decode(msg_encoded).decode()

                # Display the received message
                self.chat_display.config(state='normal')
                if msg_decoded.startswith("[Private"):
                    self.chat_display.insert(tk.END, msg_decoded + "\n", "private")

                elif msg_decoded.startswith("[Server"):
                    self.chat_display.insert(tk.END, msg_decoded + "\n", "server")

                else:
                    self.chat_display.insert(tk.END, msg_decoded + "\n", "other")
                self.chat_display.config(state='disabled')
                self.chat_display.yview(tk.END)
            except:
                break

    def send_message(self, event=None):
        # Send a message to the server
        msg = self.msg_entry.get()
        if msg:
            # Display the send message in the chat window with "You:" prefix in "Courier New" font
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"You: {msg}\n", "user")
            self.chat_display.config(state='disabled')
            self.chat_display.yview(tk.END)

            # Send the message to the server
            self.client_socket.send(base64.b64encode(msg.encode()))
            self.msg_entry.delete(0, tk.END)

        if msg.lower() == "/logout":
            self.client_socket.close()
            self.root.quit()

if __name__ == "__main__":
    # Create the main window and start the application
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
