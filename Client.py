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
            msg_encoded = client_socket.recv(1024)
            msg_decoded = base64.b64decode(msg_encoded).decode()  # Decode message from server
            if msg_decoded:
                if msg_decoded.startswith("[Server] Username already taken. ") or msg_decoded.startswith("[Server] Username is not allowed.") or msg_decoded.startswith("[Server] Username contains non-printable characters."):
                    continue

                # Clears the current line and ensures the cursor is reset
                sys.stdout.write("\r" + " " * 50 + "\r") # Clear line
                sys.stdout.flush()

                if msg_decoded.startswith(f"[Private "):
                    print(Private_Messages_Color + msg_decoded)  # Private Nachricht in Magenta

                elif msg_decoded.startswith(f"[Server"):
                    print(Server_Color + msg_decoded)  # Server Nachrichten

                elif msg_decoded.startswith(username + ":"):
                    print(Own_Messages_Color + msg_decoded)  # Eigene Nachrichten in Grün

                else:
                    print(Other_Messages_Color + msg_decoded)  # Nachrichten von anderen in Blau

                if "[Server] You have successfully logged out." != msg_decoded:
                    sys.stdout.write("> ")  # Eingabezeile erneut anzeigen
                    sys.stdout.flush()
                else:
                    break  # Schleife beenden, wenn der Client abgemeldet wurde

        except:
            print(Error_Color + "[CONNECTION TO SERVER LOST]")  # Verbindungsverlust anzeigen
            client_socket.close()  # Socket schließen
            break
    return

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Server_Ip, Server_Port))  # Connect to server

# Receive message from server (enter username)
print(base64.b64decode(client.recv(1024)).decode(), end=" ")
client_username = input()
client.send(base64.b64encode(client_username.encode()))  # Send username to server

# Receive welcome message
print(Server_Color + base64.b64decode(client.recv(1024)).decode())

# Start thread for incoming messages
thread = threading.Thread(target=receive_messages, args=(client, client_username))
thread.start()

# Send messages
while True:
    msg = input("> ")

    if msg.lower() == "/logout":
        client.send(base64.b64encode(msg.encode()))  # Abmeldung an den Server senden
        break  # Eingabeschleife beenden und Client schließen

    else:
        client.send(base64.b64encode(msg.encode()))  # Nachricht an den Server senden

# Warten bis der Thread beendet ist
thread.join()
client.close()  # Client schließen
