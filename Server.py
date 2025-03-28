import socket
import threading
import base64


clients = {}  # Stores {Socket: Username}
server_ip = "0.0.0.0"
server_port = 12345

# If the user tries to enter a username that is in the list, the server will ask the user to enter a new one
Unallowed_usernames: list[str] = []

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")  # Display new connection
    username = ""

    while username == "":
        try:
            # Receive username from client
            client_socket.send(base64.b64encode("Enter your username:".encode()))
            username = base64.b64decode(client_socket.recv(1024)).decode().strip()

            if not username.lower().isprintable():
                client_socket.send(base64.b64encode("Usernames cant inlcud not printable characters".encode()))
                username = ""

            if len(username) > 20:
                client_socket.send(base64.b64encode("Username is to long".encode()))
                username = ""

        except base64.binascii.Error:
            client_socket.send(base64.b64encode("You have to encode your massage in base64".encode()))
            username = ""

        # Check if the username is allowed
        while username.lower() in Unallowed_usernames:
            if not username.isprintable():
                client_socket.send(base64.b64encode("[Server] Username contains non-printable characters.".encode()))
                continue

            client_socket.send(base64.b64encode(f"[Server] Username is not allowed. Please Send a newone.\n"
                                                f"Unalowed usernammes {Unallowed_usernames}".encode()))
            username = base64.b64decode(client_socket.recv(1024)).decode().strip()


        # Check if the username is unique, otherwise the user gets another chance to choose a unique username or the connection is closed
        while username in clients.values():
            client_socket.send(base64.b64encode("[Server] Username already taken. Please choose another username:".encode()))
            username = base64.b64decode(client_socket.recv(1024)).decode().strip()

    clients[client_socket] = username
    print(f"[LOGIN] {username} has connected.") # Display login

    # Send welcome message
    client_socket.send(base64.b64encode(f"[Server] Welcome, {username}! \n/help to see a list of commands".encode()))

    while True:
        try:
            msg = base64.b64decode(client_socket.recv(1024)).decode() # Decode message from client
            if not msg:
                break

            if not msg.isprintable():
                client_socket.send(base64.b64encode("[Client Error] Message contains non-printable characters.".encode()))
                continue

            # Help command: for list of all commands and help with private messages
            if msg.lower() == "/help":
                for client in clients:
                    if client == client_socket:
                        client_socket.send(base64.b64encode(
                        "[Server]\n "
                        "/help shows this view\n "
                        "/logout logs you out\n "
                        "/online shows who is online\n "
                        "@[username] sends a Private Message".encode()))

            # Logout command: If the user enters "/logout", they will be logged out
            if msg.lower() == "/logout":
                client_socket.send(base64.b64encode("[Server] You have successfully logged out.".encode()))
                print(f"[LOGOUT] {username} has logged out.") # Display logout in Logs

                # Send message to all clients
                for client in clients:
                    if client != client_socket:
                        client.send(base64.b64encode(f"[Server] {username} has logged out.".encode()))
                break

            # Who is online
            if msg.lower() == "/online":
                online_users = ", ".join(clients.values())
                client_socket.send(base64.b64encode(f"Online users: {online_users}".encode()))
                continue

            # Private message: Check if the message starts with @username those won't be in the Logs
            if msg.startswith("@"):
                target_username = msg.split(" ")[0][1:]  # Username after @
                private_msg = " ".join(msg.split(" ")[1:])  # Text of the message

                # Send message only to the specified user
                for client, name in clients.items():
                    if name == target_username:
                        client.send(base64.b64encode(f"[Private from {username}]: {private_msg}".encode()))
                        break
                continue

            # Error message: If a client has an error, try to send an error message to the server
            if msg.startswith("[Client Error]"):
                print(f"{msg} Error From {username}")

            else:
                # Forward message to all other clients
                for client in clients:
                    if client != client_socket:
                        client.send(base64.b64encode(f"{username}: {msg}".encode()))

        except:
            break

    print(f"[DISCONNECT] {username} has disconnected.") # Display disconnection in the Logs
    del clients[client_socket] # Remove user
    client_socket.close() # Close connection to client

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))
server.listen(5) # Essentially the queue for requests
print("[SERVER] Waiting for connections...") # Display waiting for connections

while True:
    socket_client, address = server.accept()
    thread = threading.Thread(target= handle_client, args= (socket_client, address))
    thread.start()
