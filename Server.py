import socket
import threading

clients = {}  # Speichert {Socket: Benutzername}
server_ip = "0.0.0.0"
server_port = 12345

def handle_client(client_socket, addr):
    print(f"[NEUE VERBINDUNG] {addr} verbunden.")

    # Benutzername vom Client empfangen
    client_socket.send("Gib deinen Benutzernamen ein:".encode())
    username = client_socket.recv(1024).decode().strip()

    if username in clients.values():
        client_socket.send("Benutzername bereits vergeben. Bitte einen anderen Benutzernamen wählen:".encode())
        username = client_socket.recv(1024).decode().strip()
        if username in clients.values():
            client_socket.send("Benutzername bereits vergeben. Verbindung wird geschlossen.".encode())
            client_socket.close()
            return

    clients[client_socket] = username
    print(f"[LOGIN] {username} hat sich verbunden.")

    # Begrüßungsnachricht senden
    client_socket.send(f"Willkommen, {username} \n/help".encode())

    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break

            # Logout-Befehl: Wenn der Benutzer "!logout" eingibt, wird er abgemeldet
            if msg.lower() == "/logout":
                client_socket.send("[Server] Du hast dich erfolgreich abgemeldet.".encode())
                print(f"[LOGOUT] {username} hat sich abgemeldet.")

                # Nachricht an alle Clients senden
                for client in clients:
                    if client != client_socket:
                        client.send(f"[Server] {username} hat sich abgemeldet.".encode())
                break

            # Wer ist online
            if msg.lower() == "/online":
                online_users = ", ".join(clients.values())
                client_socket.send(f"Online Benutzer: {online_users}".encode())
                continue

            # Private Nachricht: Prüfen, ob die Nachricht mit @Benutzername beginnt
            if msg.startswith("@"):
                target_username = msg.split(" ")[0][1:]  # Benutzername nach @
                private_msg = " ".join(msg.split(" ")[1:])  # Der Text der Nachricht

                # Nachricht nur an den angegebenen Benutzer senden
                for client, name in clients.items():
                    if name == target_username:
                        client.send(f"[Privat von {username}]: {private_msg}".encode())
                        break
                continue

            # Error Nachricht: Wenn ein Client einen Fehler hat, wird versucht eine Error Nachricht and den Server zu schicken
            if msg.startswith("[Client Error]"):
                print(f"{msg} Error From {username}")

            if msg.lower() == "/help":
                for client in clients:
                    if client == client_socket:
                        client_socket.send(
                        "[Server]\n /help shows this view\n /logout logs you out\n /online shows who is online\n @[username] sends a Private Message".encode())

            else:
                print(f"[{username}] {msg}")
                # Nachricht an alle anderen Clients weiterleiten
                for client in clients:
                    if client != client_socket:
                        client.send(f"{username}: {msg}".encode())

        except:
            break

    print(f"[ABMELDUNG] {username} hat die Verbindung getrennt.")
    del clients[client_socket]  # Benutzer entfernen
    client_socket.close() # schließt die Verbindung zum Client


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))
server.listen(5) # Basically die Warteschlange für anfragen

print("[SERVER] Wartet auf Verbindungen...")
print(f"[SERVER] Ip: {server_ip} Port: {server_port}")

while True:
    client_socket, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.start()
