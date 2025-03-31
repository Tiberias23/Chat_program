# Chat Program

## Overview

This project is a simple chat program that allows users to communicate with each other in real-time. It is built using Python and leverages socket programming to enable communication between clients and the server.

## Features

- **Real-time chat**: Communicate with multiple users in real-time.
- **Private messages**: Send direct messages to specific users using `@[username]`.
- **Group chat**: Broadcast messages to all connected users.
- **Message encoding with Base64**: Ensures proper message formatting and transmission.

## Limitations

The following features are not implemented in this version of the chat program:
- User authentication
- Message encryption
- File sharing
- Message history
- User status (e.g., online/offline)
- User profiles
- Blocking or banning users
- User roles and permissions
- Registration and login
- Notifications
- User interface (except for the GUI version in another branch)

This project is in **early development** and was created as a learning exercise to explore networking concepts in Python. Many features are intentionally omitted to keep the implementation simple.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/YourUsername/Chat_program.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Chat_program
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the server:
    ```bash
    python server.py
    ```
2. Start the client:
    ```bash
    python client.py
    ```

### Notes:
- If you prefer a graphical user interface (GUI) for the client, you can use the `client_gui.py` file available in another branch.
- To run the client on a different machine, update the `host` variable in the `client.py` file to the server's IP address before running it.
- If you want to create your own client, ensure that all messages are encoded and decoded using Base64.

## Logging

To log every message sent and received, uncomment the relevant lines in the `Server.py` file:
- Uncomment **line 94** to log incoming messages.
- Uncomment **line 118** to log outgoing messages.

## Contributing

Contributions are welcome! If you'd like to contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## Contact

If you have any questions, suggestions, or issues, please open an issue on the repository with the appropriate tags (e.g., `question`, `enhancement`, or `bug`).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for checking out this project! Feedback and contributions are greatly appreciated.

