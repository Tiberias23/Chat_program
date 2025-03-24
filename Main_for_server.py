import socket
import threading

clients = {}  # Stores {Socket: Username}

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")  # Display new connection

    # Receive username from client
    client_socket.send("Enter your username:".encode())
    username = client_socket.recv(1024).decode().strip()

    # Check if the username is unique, otherwise the user gets another chance to choose a unique username or the connection is closed
    if username in clients.values():
        client_socket.send("Username already taken. Please choose another username:".encode())
        username = client_socket.recv(1024).decode().strip()
        if username in clients.values():
            client_socket.send("Username already taken. Connection will be closed.".encode())
            client_socket.close()
            return

    clients[client_socket] = username
    print(f"[LOGIN] {username} has connected.") # Display login

    # Send welcome message
    client_socket.send(f"Welcome, {username}!".encode())

    while True:
        try:
            msg = client_socket.recv(1024).decode() # Receive message from client
            if not msg:
                break

            # Logout command: If the user enters "!logout", they will be logged out
            if msg.lower() == "!logout":
                client_socket.send("[Server] You have successfully logged out.".encode())
                print(f"[LOGOUT] {username} has logged out.") # Display logout in Logs

                # Send message to all clients
                for client in clients:
                    if client != client_socket:
                        client.send(f"[Server] {username} has logged out.".encode())
                break

            # Who is online
            if msg.lower() == "/online":
                online_users = ", ".join(clients.values())
                client_socket.send(f"Online users: {online_users}".encode())
                break

            # Private message: Check if the message starts with @username those won't be in the Logs
            if msg.startswith("@"):
                target_username = msg.split(" ")[0][1:]  # Username after @
                private_msg = " ".join(msg.split(" ")[1:])  # Text of the message

                # Send message only to the specified user
                for client, name in clients.items():
                    if name == target_username:
                        client.send(f"[Private from {username}]: {private_msg}".encode())
                        break
                continue

            # Error message: If a client has an error, try to send an error message to the server
            if msg.startswith("[Client Error]"):
                print(f"{msg} Error From {username}")

            else:
                # Log open messages, not private messages
                print(f"[{username}] {msg}")

                # Forward message to all other clients
                for client in clients:
                    if client != client_socket:
                        client.send(f"{username}: {msg}".encode())

        except:
            break

    print(f"[DISCONNECT] {username} has disconnected.") # Display disconnection in the Logs
    del clients[client_socket] # Remove user
    client_socket.close() # Close connection to client

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 12345))
server.listen(5) # Essentially the queue for requests

print("[SERVER] Waiting for connections...") # Display waiting for connections

while True:
    client_socket, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.start()

