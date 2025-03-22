import socket
import threading
import sys
from colorama import init, Fore

init(autoreset=True)  # Stellt sicher, dass Farben nach jeder Zeile zurückgesetzt werden

Server_Farbe = Fore.YELLOW
Fehler_Farbe = Fore.RED
Eigene_Nachrichten_Farbe = Fore.GREEN
Andere_Nachrichten_Farbe = Fore.BLUE


def receive_messages(client_socket, username):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                sys.stdout.write("\r" + " " * 50 + "\r")

                # Eigene Nachrichten grün anzeigen, andere blau
                if msg.startswith(f"[Privat von {username}]:"):
                    print(Fore.MAGENTA + msg)  # Private Nachrichten in Magenta

                elif msg.startswith(username + ":"):
                    print(Eigene_Nachrichten_Farbe + msg)  # Eigene Nachrichten

                else:
                    print(Andere_Nachrichten_Farbe + msg)  # Nachrichten von anderen

                sys.stdout.write("> ")  # Eingabezeile neu anzeigen
                sys.stdout.flush()
        except:
            print(Fehler_Farbe + "[VERBINDUNG ZUM SERVER VERLOREN]")
            client_socket.close()
            break


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 12345))  # Verbindung zum Server

# Nachricht vom Server empfangen (Benutzernamen eingeben)
print(client.recv(1024).decode(), end=" ")
username = input()
client.send(username.encode())  # Benutzername an Server senden

# Begrüßungsnachricht empfangen
print( Server_Farbe + client.recv(1024).decode())

# Starte Thread für eingehende Nachrichten
thread = threading.Thread(target=receive_messages, args=(client, username))
thread.start()

# Nachrichten senden
while True:
    msg = input("> ")
    client.send(msg.encode())  # Nachricht an Server senden
