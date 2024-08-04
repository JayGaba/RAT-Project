# Remote Access Trojan (RAT) Project

## Description

This project consists of a simple yet powerful Remote Access Trojan (RAT) written in Python. It allows a user to remotely control a victim's machine over a network, providing functionalities such as file upload/download, keylogging, and command execution.

## Features

- **Remote Command Execution**: Execute system commands on the target machine.
- **File Upload and Download**: Transfer files between the attacker and the target machine.
- **Keylogging**: Capture keystrokes on the target machine.
- **Credential Dumping**: Extract credentials from the target machine using the LaZagne tool.
- **Persistent Connection**: Maintains a persistent connection with the target machine.
- **Change Working Directory**: Change the current working directory on the target machine.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/RAT-Project.git
   cd RAT-Project
   
2. **Install dependencies:**
   
   Ensure you have Python installed. Install the required libraries using requirements.txt:
   ```sh
   pip install -r requirements.txt
3. **Run the Server:**

   On the attacker's machine:
   ```sh
   python server.py
4. **Run the Client:**

   On the victim's machine:
    ```sh
    python client.py
    ```

## Usage

1. **Start the Listener:** Run server.py on your machine. It will start listening for incoming connections.
2. **Deploy the Backdoor:** Execute client.py on the target machine to establish a connection with your listener.
3. **Interact with the Target:** Use the provided commands to interact with the target machine.

## Commands:

- **upload <path>**: Upload a file to the target machine.
- **get <path>**: Download a file from the target machine.
- **keyscan_start**: Start capturing keystrokes.
- **keyscan_dump**: Stop capturing keystrokes and download the keylog file.
- **creds_dump**: Dump credentials from the target machine.
- **exit**: Terminate the connection.

## Code Overview
### server.py
The server.py script sets up a listener that waits for incoming connections. Once a connection is established, it allows the user to send commands to the target machine and receive responses.

### client.py
The client.py script connects to the attacker's machine and waits for commands. It supports various functionalities, including file upload/download, command execution, keylogging, and credential dumping.

## Future Enhancements
- **Encryption**: Implement encryption for data transmission to enhance security.
- **Persistence**: Add mechanisms to ensure the client script runs automatically on startup.
- **Advanced Keylogging**: Improve keylogging to capture more complex key combinations.
- **Anti-Detection**: Implement techniques to evade detection by antivirus software.
- **Access Webcam**: Add the functionality to access webcam of the victim machine.

## Disclaimer
This project is for educational purposes only. Use it responsibly and only on systems you own or have permission to test.
