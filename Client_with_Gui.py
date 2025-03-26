import socket
import threading
import base64
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Server Settings have to match the ip and Port from the Server
SERVER_IP: str = "127.0.0.1"
SERVER_PORT: int = 12345

# Change this like you want it does only effect the look of the Chat
# Font stuff
font_size: int = 11
font: str = "Arial"

# Massage stuff
user_color: str = "green"
other_color: str = "gray"
server_color: str = "orange"
private_color: str = "magenta"

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("250x125")  # Start mit Login-Fenster

        self.username: str = ""
        self.dark_mode: bool = False  # Dark Mode ist zuerst aus
        self.first_click: bool = True  # Erster Klick ist speziell für Dark Mode
        self.bg_colors: list[str] = ["white", "lightgray", "lightblue", "lightgreen", "lightyellow", "lightpink"]
        self.bg_index: int = 0  # Start mit erster Farbe

        # Login Frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()
        self.username_entry.bind("<Return>", lambda event: self.connect_to_server())

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.connect_to_server)
        self.login_button.pack()

        # Chat Frame (zunächst versteckt)
        self.chat_frame = tk.Frame(self.root, bg=self.bg_colors[self.bg_index])

        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, state='disabled', width=50, height=20, font=(font, font_size))
        self.chat_display.pack(pady=10)

        self.msg_entry = tk.Entry(self.chat_frame, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.msg_entry.bind("<Return>", self.send_message)

        self.placeholder_text: str = "/help for commands"
        self.msg_entry.insert(0, self.placeholder_text)
        self.msg_entry.config(fg="grey")

        self.msg_entry.bind("<FocusIn>", self.clear_placeholder)
        self.msg_entry.bind("<FocusOut>", self.restore_placeholder)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, pady=10, padx=10)

        # Dark Mode & Background Color Button
        self.bg_button = tk.Button(self.chat_frame, text="Change Background", command=self.toggle_background)
        self.bg_button.pack(pady=10, padx=10)

        # Textfarben für Nachrichten
        self.chat_display.tag_configure("user", font=(font, font_size), foreground=user_color)
        self.chat_display.tag_configure("other", font=(font, font_size), foreground=other_color)
        self.chat_display.tag_configure("server", font=(font, font_size), foreground=server_color)
        self.chat_display.tag_configure("private", font=(font, font_size), foreground=private_color)

        self.client_socket = None


    def clear_placeholder(self, event):
        if self.msg_entry.get() == self.placeholder_text:
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.config(fg="black")


    def restore_placeholder(self, event):
        if not self.msg_entry.get():
            self.msg_entry.insert(0, self.placeholder_text)
            self.msg_entry.config(fg="grey")


    def toggle_background(self):
        """Erster Klick aktiviert Dark Mode, danach wird durch Farben rotiert."""
        if self.first_click:
            self.first_click: bool = False
            self.dark_mode: bool = True
            self.activate_dark_mode()
        else:
            self.dark_mode: bool = False
            self.change_bg_color()


    def activate_dark_mode(self):
        """Dark Mode aktivieren."""
        self.chat_frame.config(bg="black")
        self.chat_display.config(bg="black", fg="white")
        self.msg_entry.config(bg="black", fg="white")
        self.send_button.config(bg="gray", fg="white")
        self.bg_button.config(bg="gray", fg="white", text="Change Background")


    def change_bg_color(self):
        """Rotiert durch helle Hintergrundfarben."""
        if not self.dark_mode:
            self.bg_index = (self.bg_index + 1) % len(self.bg_colors)
            new_color = self.bg_colors[self.bg_index]

            self.chat_frame.config(bg=new_color)
            self.chat_display.config(bg=new_color, fg="black")
            self.msg_entry.config(bg=new_color, fg="black")
            self.send_button.config(bg=new_color)
            self.bg_button.config(bg=new_color, text="Change Background")


    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.username = self.username_entry.get()

            if not self.username:
                messagebox.showerror("Error", "Username cannot be empty!")
                return

            self.client_socket.send(base64.b64encode(self.username.encode()))

            self.login_frame.pack_forget()
            self.chat_frame.pack()
            self.root.geometry("")  # Größe automatisch anpassen

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))


    def receive_messages(self):
        while True:
            try:
                msg_encoded: str = self.client_socket.recv(1024)
                if not msg_encoded:
                    break
                msg_decoded: str = base64.b64decode(msg_encoded).decode()

                self.chat_display.config(state='normal')
                if msg_decoded.startswith("[Private"):
                    self.chat_display.insert(tk.END, msg_decoded + "\n", "private")
                elif msg_decoded.startswith("[Server]"):
                    self.chat_display.insert(tk.END, msg_decoded + "\n", "server")
                elif msg_decoded == "Enter your username:":
                    continue
                else:
                    self.chat_display.insert(tk.END, msg_decoded + "\n", "other")

                self.chat_display.config(state='disabled')
                self.chat_display.yview(tk.END)
            except:
                break


    def send_message(self, event=None):
        msg: str = self.msg_entry.get()
        if msg:
            if msg.isprintable():
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, f"You: {msg}\n", "user")
                self.chat_display.config(state='disabled')
                self.chat_display.yview(tk.END)

                self.client_socket.send(base64.b64encode(msg.encode()))
                self.msg_entry.delete(0, tk.END)
            else:
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, "message contains not printable objects\n", "private")

        if msg.lower() == "/logout":
            self.client_socket.close()
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
