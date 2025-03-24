import time
import socket
import threading
import sys
import base64
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
            msg = client_socket.recv(1024)
            msg = base64.b64decode(msg).decode()  # Decode message from server
            if msg:
                if msg.startswith("Username already taken. "):
                    continue

                # Clears the current line and ensures the cursor is reset
                sys.stdout.write("\r" + " " * 50 + "\r") # Clear line
                sys.stdout.flush()

                if msg.startswith(f"[Private "):
                    print(Private_Messages_Color + msg)  # Private Nachricht in Magenta

                elif msg.startswith(f"[Server"):
                    print(Server_Color + msg)  # Server Nachrichten

                elif msg.startswith(username + ":"):
                    print(Own_Messages_Color + msg)  # Eigene Nachrichten in Grün

                else:
                    print(Other_Messages_Color + msg)  # Nachrichten von anderen in Blau

                if "[Server] You have successfully logged out." in msg:
                    break  # Schleife bei Abmelde-Nachricht beenden

                sys.stdout.write("> ")  # Eingabezeile erneut anzeigen
                sys.stdout.flush()

        except Exception as e:
            print(Error_Color + "[CONNECTION TO SERVER LOST]")  # Verbindungsverlust anzeigen
            client_socket.close()  # Socket schließen
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Server_Ip, Server_Port))  # Connect to server

# Receive message from server (enter username)
print(base64.b64decode(client.recv(1024)).decode(), end=" ")
username = input()
client.send(base64.b64encode(username.encode()))  # Send username to server

# Receive welcome message
print(Server_Color + base64.b64decode(client.recv(1024)).decode())

# Start thread for incoming messages
thread = threading.Thread(target=receive_messages, args=(client, username))
thread.start()

# Send messages
while True:
    msg = input("> ")

    if msg.lower() == "!logout":
        client.send(base64.b64encode(msg.encode()))  # Abmeldung an den Server senden
        time.sleep(1)
        client.close()
        break  # Eingabeschleife beenden und Client schließen

    else:
        client.send(base64.b64encode(msg.encode()))  # Nachricht an den Server senden
