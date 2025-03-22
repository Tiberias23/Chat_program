import socket
import threading

clients = {}  # Speichert {Socket: Benutzername}


def handle_client(client_socket, addr):
    print(f"[NEUE VERBINDUNG] {addr} verbunden.")

    # Benutzername vom Client empfangen
    client_socket.send("Gib deinen Benutzernamen ein:".encode())
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

            # Logout-Befehl: Wenn der Benutzer "!logout" eingibt, wird er abgemeldet
            if msg.lower() == "!logout":
                client_socket.send("[Server] Du hast dich erfolgreich abgemeldet.".encode())
                print(f"[LOGOUT] {username} hat sich abgemeldet.")

                # Nachricht an alle Clients senden
                for client in clients:
                    if client != client_socket:
                        client.send(f"{username} hat sich abgemeldet.".encode())
                break

            # Private Nachricht: Prüfen, ob die Nachricht mit @Benutzername beginnt
            if msg.startswith("@"):
                target_username = msg.split(" ")[0][1:]  # Benutzername nach @
                private_msg = " ".join(msg.split(" ")[1:])  # Der Text der Nachricht

                # Nachricht nur an den angegebenen Benutzer senden
                for client, name in clients.items():
                    if name == target_username:
                        client.send(f"[Privat von {username}]: {private_msg}".encode())
                        break

            # Error Nachricht: Wenn ein Client einen Fehler hat, wird versucht eine Error Nachricht and den Server
            if msg.startswith("[Client Error]"):
                print(f"{msg} Error From {username}")

            else:
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

print("[SERVER] Wartet auf Verbindungen...")

while True:
    client_socket, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.start()
