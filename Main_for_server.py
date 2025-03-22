import socket
import threading

clients = {}  # Speichert {Socket: Benutzername}


def handle_client(client_socket, addr):
    print(f"[NEUE VERBINDUNG] {addr} verbunden.")

    # Benutzername vom Client empfangen
    client_socket.send("Gib deinen Benutzernamen ein\n".encode())
    username = client_socket.recv(1024).decode().strip()

    clients[client_socket] = username
    print(f"[LOGIN] {username} hat sich verbunden.")

    # Begrüßungsnachricht senden
    client_socket.send(f"Willkommen, {username}!".encode())

    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break

            print(f"[{username}] {msg}")

            # Nachricht an alle anderen Clients weiterleiten
            for client in clients:
                if client != client_socket:
                    client.send(f"{username}: {msg}".encode())

        except:
            break

    print(f"[ABMELDUNG] {username} hat die Verbindung getrennt.")
    del clients[client_socket]  # Benutzer entfernen
    client_socket.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 12345))
server.listen(5)

print("[SERVER GESTARTET] Wartet auf Verbindungen...")

while True:
    client_socket, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.start()
