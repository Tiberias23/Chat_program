import time
import socket
import threading
import sys
from colorama import init, Fore

init(autoreset=True)  # Stellt sicher, dass Farben nach jeder Zeile zurückgesetzt werden

# Farben für verschiedene Nachrichten änder dies so wie du willst die Bibliothek dafür ist colorama
Server_Farbe = Fore.YELLOW
Fehler_Farbe = Fore.RED
Eigene_Nachrichten_Farbe = Fore.GREEN
Private_Nachrichten_Farbe = Fore.MAGENTA
Andere_Nachrichten_Farbe = Fore.CYAN

# This has to be the same as the stuff in Server.Binde() in the Server.py
Server_Ip = "127.0.0.1"
Server_Port = 12345

def receive_messages(client_socket, username):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                if msg.startswith("Benutzername bereits vergeben. "):
                    continue

                # Löscht die aktuelle Zeile und sorgt dafür, dass der Cursor zurückgesetzt wird
                sys.stdout.write("\r" + " " * 50 + "\r")  # Zeile löschen
                sys.stdout.flush()

                if msg.startswith(f"[Privat "):
                    print(Private_Nachrichten_Farbe + msg)  # Private Nachricht in Magenta

                elif msg.startswith(f"[Server"):
                    print(Server_Farbe + msg)  # Server Nachrichten

                elif msg.startswith(username + ":"):
                    print(Eigene_Nachrichten_Farbe + msg)  # Eigene Nachrichten in Grün

                else:
                    print(Andere_Nachrichten_Farbe + msg)  # Nachrichten von anderen in Blau

                if "[Server] Du hast dich erfolgreich abgemeldet." in msg:
                    break  # Beende die Schleife bei Logout-Nachricht

                sys.stdout.write("> ")  # Eingabezeile neu anzeigen
                sys.stdout.flush()

        except Exception as e:
            print(Fehler_Farbe + "[VERBINDUNG ZUM SERVER VERLOREN]")
            client_socket.send(f"[Client Error] Client had error: {e}")
            client_socket.close()
            break


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Server_Ip, Server_Port))  # Verbindung zum Server

# Nachricht vom Server empfangen (Benutzernamen eingeben)
print(client.recv(1024).decode(), end=" ")
username = input()
client.send(username.encode())  # Benutzername an Server senden

# Begrüßungsnachricht empfangen
print(Server_Farbe + client.recv(1024).decode())

# Starte Thread für eingehende Nachrichten
thread = threading.Thread(target=receive_messages, args=(client, username))
thread.start()

# Nachrichten senden
while True:
    msg = input("> ")

    if msg.lower() == "!logout":
        client.send(msg.encode())  # Logout an Server senden
        time.sleep(1)
        client.close()
        break # Beende die Eingabe-Schleife

    else:
        client.send(msg.encode()) # Nachricht an Server senden
