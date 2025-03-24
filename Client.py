import time
import socket
import threading
import sys
from colorama import init, Fore

init(autoreset=True)  # Ensures that colors are reset after each line

# Colors for different messages, change them as desired, the library used is colorama
Server_Color = Fore.YELLOW
Error_Color = Fore.RED
Own_Messages_Color = Fore.GREEN
Private_Messages_Color = Fore.MAGENTA
Other_Messages_Color = Fore.CYAN

# This must match the settings in Server.bind() in Server.py
Server_Ip = "127.0.0.1"
Server_Port = 12345

def receive_messages(client_socket, username):
    while True:
        try:
            msg = client_socket.recv(1024).decode() # Receive message from server
            if msg:
                if msg.startswith("Username already taken. "):
                    continue

                # Clears the current line and ensures the cursor is reset
                sys.stdout.write("\r" + " " * 50 + "\r") # Clear line
                sys.stdout.flush()

                if msg.startswith(f"[Private "):
                    print(Private_Messages_Color + msg) # Private message in magenta

                elif msg.startswith(f"[Server"):
                    print(Server_Color + msg) # Server messages

                elif msg.startswith(username + ":"):
                    print(Own_Messages_Color + msg) # Own messages in green

                else:
                    print(Other_Messages_Color + msg) # Messages from others in blue

                if "[Server] You have successfully logged out." in msg:
                    break # End loop on logout message

                sys.stdout.write("> ") # Display input line again
                sys.stdout.flush()

        except Exception as e:
            print(Error_Color + "[CONNECTION TO SERVER LOST]") # Display connection loss
            client_socket.close() # Close socket
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Server_Ip, Server_Port)) # Connect to server

# Receive message from server (enter username)
print(client.recv(1024).decode(), end=" ")
username = input()
client.send(username.encode()) # Send username to server

# Receive welcome message
print(Server_Color + client.recv(1024).decode())

# Start thread for incoming messages
thread = threading.Thread(target=receive_messages, args=(client, username))
thread.start()

# Send messages
while True:
    msg = input("> ")

    if msg.lower() == "!logout":
        client.send(msg.encode()) # Send logout to server
        time.sleep(1)
        client.close()
        break # End input loop and close client

    else:
        client.send(msg.encode()) # Send message to server
