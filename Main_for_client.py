import socket
import threading
import sys
from colorama import init, Fore

init(autoreset=True)  # Stellt sicher, dass Farben nach jeder Zeile zurückgesetzt werden

# Farben für verschiedene Nachrichten
Server_Farbe = Fore.YELLOW
Fehler_Farbe = Fore.RED
Eigene_Nachrichten_Farbe = Fore.GREEN
Andere_Nachrichten_Farbe = Fore.BLUE

Server_Ip = "127.0.0.1"
Server_Port = 12345

def receive_messages(client_socket, username):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                # Löscht die aktuelle Zeile und sorgt dafür, dass der Cursor zurückgesetzt wird
                sys.stdout.write("\r" + " " * 50 + "\r")  # Zeile löschen
                sys.stdout.flush()

                # Eigene Nachrichten grün anzeigen, Private Nachrichten in Magenta, andere blau
                if msg.startswith(f"[Privat von "):
                    print(Fore.MAGENTA + msg)  # Private Nachricht in Magenta
                elif msg.startswith(username + ":"):
                    print(Eigene_Nachrichten_Farbe + msg)  # Eigene Nachrichten in Grün
                else:
                    print(Andere_Nachrichten_Farbe + msg)  # Nachrichten von anderen in Blau

                sys.stdout.write("> ")  # Eingabezeile neu anzeigen
                sys.stdout.flush()
        except:
            print(Fehler_Farbe + "[VERBINDUNG ZUM SERVER VERLOREN]")
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
        sys.stdout.write("\r" + " " * 50 + "\r")  # Löscht die Eingabeaufforderung
        sys.stdout.flush()
        print(Fore.YELLOW + "Du hast dich erfolgreich abgemeldet.")  # Nachricht nur lokal
        break  # Beende die Eingabe-Schleife und verlasse das Programm

    else:
        client.send(msg.encode())  # Nachricht an Server senden

# Wenn Logout durchgeführt wurde, den Cursor verschwinden lassen
sys.stdout.write("\r" + " " * 50 + "\r")  # Löscht die Eingabeaufforderung endgültig
sys.stdout.flush()
