import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                print(msg)
        except:
            print("[VERBINDUNG ZUM SERVER VERLOREN]")
            client_socket.close()
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 12345))  # Verbindung zum Server

# Nachricht vom Server empfangen (Benutzernamen eingeben)
print(client.recv(1024).decode(), end=" ")
username = input()
client.send(username.encode())  # Benutzername an Server senden

# Begrüßungsnachricht empfangen
print(client.recv(1024).decode())

# Starte Thread für eingehende Nachrichten
thread = threading.Thread(target=receive_messages, args=(client,))
thread.start()

# Nachrichten senden
while True:
    msg = input("> ")
    client.send(msg.encode())  # Nachricht an Server senden
