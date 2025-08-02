import socket
import threading
import base64
import binascii
import re
from typing import Dict, List, Tuple

# Define a regex pattern for escape sequences
ESCAPE_SEQUENCE_PATTERN: re.Pattern = re.compile(r'\x1b\[[0-9;=]*[a-zA-Z]')

SERVER_IP: str = "0.0.0.0"
SERVER_PORT: int = 12345

# If the user tries to enter a username that is in the list, the server will ask the user to enter a new one
Unallowed_usernames: List[str] = []  # Ensure all are lowercase
clients: Dict[socket.socket, str] = {}  # Maps client sockets to usernames


def handle_login(client_socket: socket.socket) -> None:
    username: str = ""

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

    clients[client_socket] = username


def handle_command(client_socket: socket.socket, username: str, msg: str) -> None:
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
        online_users: str = ", ".join(clients.values())
        client_socket.send(base64.b64encode(f"Online users: {online_users}".encode()))
        return

    if msg.startswith("@"):
        target_username: str = msg.split(" ")[0][1:]  # Username after @
        private_msg: str = " ".join(msg.split(" ")[1:])  # Text of the message

        user_is_reachable: bool = False
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


def handle_client(client_socket: socket.socket, addr: Tuple[str, int]) -> None:
    """Handles the client connection."""

    print(f"[NEW CONNECTION] {addr} connected.")  # Display new connection

    try:
        handle_login(client_socket)  # Handle login for the client
        username: str = clients.get(client_socket, "")  # Get the username of the client

        print(f"[LOGIN] {username} has connected.")  # Display login

        # Send welcome message
        client_socket.send(base64.b64encode(f"[Server] Welcome, {username}! \n/help to see a list of commands".encode()))

        while True:
            try:
                msg: str = base64.b64decode(client_socket.recv(1024)).decode()  # Decode message from client
                if not msg:
                    break

                # Check for escape sequences using regex
                if ESCAPE_SEQUENCE_PATTERN.search(msg):
                    client_socket.send(base64.b64encode("[Client Error] Message contains invalid escape sequences.".encode()))
                    continue

                # Check if the message is a command
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
                print(f"[DISCONNECT] {addr} disconnected unexpectedly.")
                break

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        print(f"[DISCONNECT] {addr} disconnected.")  # Display disconnection in the Logs
        if client_socket in clients:
            del clients[client_socket]
        client_socket.close()  # Close connection to client


def main() -> None:
    server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)  # The queue for requests
    print("[SERVER] Waiting for connections...")  # Display waiting for connections

    try:
        while True:
            socket_client, address = server.accept()
            thread: threading.Thread = threading.Thread(target=handle_client, args=(socket_client, address), daemon=True)
            thread.start()
    
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    
    finally:
        server.close()
        print("[SERVER] Socket closed.")


if __name__ == "__main__":
    main()  # Start the server