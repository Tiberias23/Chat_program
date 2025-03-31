import socket
import threading
import base64
import binascii

server_ip: str = "0.0.0.0"
server_port: int = 12345

# If the user tries to enter a username that is in the list, the server will ask the user to enter a new one
Unallowed_usernames: list[str] = [] # Unallowed usernames edit it like this: Unallowed_usernames = ["admin", "root", "test"]

def handle_login(client_socket) -> None:
    username = ""

    while username == "":
        try:
            # Receive username from client
            client_socket.send(base64.b64encode("[Server] Enter your username:".encode()))
            username = base64.b64decode(client_socket.recv(1024)).decode().strip()

            if not username.isprintable():
                client_socket.send(base64.b64encode("[Server] Usernames can't include non-printable characters.".encode()))
                username = ""

            if len(username) > 20:
                client_socket.send(base64.b64encode("[Server] Username is too long.".encode()))
                username = ""

        except (binascii.Error, UnicodeDecodeError):
            client_socket.send(base64.b64encode("[Server] You have to encode your message in base64.".encode()))
            username = ""

    # Check if the username is allowed
    while username.lower() in Unallowed_usernames:
        client_socket.send(base64.b64encode(f"[Server] Username is not allowed. Please send a new one.\n"
                                            f"Unallowed usernames: {Unallowed_usernames}".encode()))
        username = base64.b64decode(client_socket.recv(1024)).decode().strip()

    # Check if the username is unique
    while username in clients.values():
        client_socket.send(base64.b64encode("[Server] Username already taken. Please choose another username:".encode()))
        username = base64.b64decode(client_socket.recv(1024)).decode().strip()

def handle_command(client_socket, username, msg) -> None:
    """
    Handles commands sent by the client.
    """
    if msg.lower() == "/help":
        client_socket.send(base64.b64encode(
            "[Server]\n"
            "/help shows this view\n"
            "/logout logs you out\n"
            "/online shows who is online\n"
            "@[username] sends a Private Message\n".encode()))
        return

    if msg.lower() == "/logout":
        client_socket.send(base64.b64encode("[Server] You have successfully logged out.".encode()))
        print(f"[LOGOUT] {username} has logged out.")  # Display logout in Logs

        for client in clients:
            if client != client_socket:
                client.send(base64.b64encode(f"[Server] {username} has logged out.".encode()))
        del clients[client_socket]
        raise ConnectionResetError  # Force disconnection after logout

    if msg.lower() == "/online":
        online_users = ", ".join(clients.values())
        client_socket.send(base64.b64encode(f"Online users: {online_users}".encode()))
        return

    if msg.startswith("@"):
        target_username = msg.split(" ")[0][1:]  # Username after @
        private_msg = " ".join(msg.split(" ")[1:])  # Text of the message

        user_is_reachable = False
        for client, name in clients.items():
            if name == target_username:
                client.send(base64.b64encode(f"[Private from {username}]: {private_msg}".encode()))
                user_is_reachable = True
                break

        if not user_is_reachable:
            client_socket.send(base64.b64encode(f"[Server] User {target_username} is not online.".encode()))
        return None

    # If the command is not recognized
    client_socket.send(base64.b64encode("[Server] Unknown command. Type /help for a list of commands.".encode()))

def handle_client(client_socket, addr) -> None:
    """Handles the client connection."""
    print(f"[NEW CONNECTION] {addr} connected.")  # Display new connection

    try:
        handle_login(client_socket)  # Handle login for the client
        username = clients.get(client_socket)  # Get the username of the client

        print(f"[LOGIN] {username} has connected.")  # Display login

        # Send welcome message
        client_socket.send(base64.b64encode(f"[Server] Welcome, {username}! \n/help to see a list of commands".encode()))

        while True:
            try:
                msg = base64.b64decode(client_socket.recv(1024)).decode()  # Decode message from client
                if not msg:
                    break

                if not msg.isprintable():
                    client_socket.send(base64.b64encode("[Client Error] Message contains non-printable characters.".encode()))
                    continue

                if msg.startswith("/") or msg.startswith("@"):  # Check if the message is a command
                    handle_command(client_socket, username, msg)
                    continue

                # Broadcast message to other clients
                for client in clients:
                    if client != client_socket:
                        client.send(base64.b64encode(f"{username}: {msg}".encode()))

            except (binascii.Error, UnicodeDecodeError):
                client_socket.send(base64.b64encode("[Server] Invalid message format.".encode()))
            except ConnectionResetError:
                break

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        print(f"[DISCONNECT] {addr} disconnected.")  # Display disconnection in the Logs
        if client_socket in clients:
            del clients[client_socket]
        client_socket.close()  # Close connection to client

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))
server.listen(5)  # The queue for requests
print("[SERVER] Waiting for connections...")  # Display waiting for connections

def main() -> None:

    while True:
        socket_client, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(socket_client, address), daemon=True)
        thread.start()

if __name__ == "__main__":
    main()  # Start the server