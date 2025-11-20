import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, Listbox

HOST = '127.0.0.1'
PORT = 55555


class ChatClient:
    def __init__(self):
        self.client_socket = None
        self.nickname = ""
        self.running = False

        self.root = tk.Tk()
        self.root.title("Student Chat Client")
        self.root.geometry("600x500")

        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=10, fill='x')

        tk.Label(top_frame, text="Nickname:").pack(side=tk.LEFT)
        self.entry_nickname = tk.Entry(top_frame)
        self.entry_nickname.pack(side=tk.LEFT, padx=10)

        self.btn_connect = tk.Button(top_frame, text="Connect", command=self.connect_to_server)
        self.btn_connect.pack(side=tk.LEFT)

        middle_frame = tk.Frame(self.root)
        middle_frame.pack(padx=10, pady=5, expand=True, fill='both')

        self.chat_area = scrolledtext.ScrolledText(middle_frame, state='disabled', width=50)
        self.chat_area.pack(side=tk.LEFT, expand=True, fill='both')

        right_frame = tk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill='y', padx=(5, 0))

        tk.Label(right_frame, text="Online Users").pack()
        self.user_listbox = Listbox(right_frame, width=20)
        self.user_listbox.pack(expand=True, fill='y')
        self.user_listbox.bind('<Double-1>', self.prepare_private_message)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(padx=10, pady=10, fill='x')

        self.entry_message = tk.Entry(bottom_frame)
        self.entry_message.pack(side=tk.LEFT, expand=True, fill='x')
        self.entry_message.bind("<Return>", self.send_public_message)

        self.btn_send = tk.Button(bottom_frame, text="Send Public", command=self.send_public_message)
        self.btn_send.pack(side=tk.RIGHT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def connect_to_server(self):
        nickname = self.entry_nickname.get()
        if not nickname:
            messagebox.showerror("Error", "Please enter a nickname.")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))

            packet = {"type": "LOGIN", "content": nickname}
            self.client_socket.send(json.dumps(packet).encode('utf-8'))

            self.nickname = nickname
            self.running = True

            self.entry_nickname.config(state='disabled')
            self.btn_connect.config(state='disabled')
            self.add_text(f"--- Connected to {HOST}:{PORT} as {nickname} ---")

            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")

    def receive_messages(self):
        while self.running:
            try:
                buffer = self.client_socket.recv(1024).decode('utf-8')
                if not buffer:
                    break

                data = json.loads(buffer)
                msg_type = data.get("type")
                content = data.get("content")
                sender = data.get("sender", "")
                timestamp = data.get("timestamp", "")

                if msg_type == "PUBLIC":
                    self.add_text(f"[{timestamp}] {sender}: {content}")

                elif msg_type == "PRIVATE":
                    self.add_text(f"[{timestamp}] [PRIVATE] {sender}: {content}")

                elif msg_type == "SYSTEM":
                    self.add_text(f"[{timestamp}] *** {content} ***")

                elif msg_type == "USER_LIST":
                    self.update_user_list(content)

            except:
                self.running = False
                break

        self.client_socket.close()

    def send_public_message(self, event=None):
        msg = self.entry_message.get()
        if not msg or not self.running:
            return

        packet = {
            "type": "PUBLIC",
            "content": msg
        }
        try:
            self.client_socket.send(json.dumps(packet).encode('utf-8'))
            self.entry_message.delete(0, tk.END)
        except:
            self.add_text("Error sending message.")

    def prepare_private_message(self, event):
        selection = self.user_listbox.curselection()
        if not selection:
            return

        target_user = self.user_listbox.get(selection[0])
        if target_user == self.nickname:
            return

        msg = simpledialog.askstring("Private Message", f"Send message to {target_user}:")
        if msg:
            packet = {
                "type": "PRIVATE",
                "target": target_user,
                "content": msg
            }
            try:
                self.client_socket.send(json.dumps(packet).encode('utf-8'))
            except:
                self.add_text("Error sending private message.")

    def update_user_list(self, users):
        self.user_listbox.delete(0, tk.END)
        for user in users:
            self.user_listbox.insert(tk.END, user)

    def add_text(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, text + "\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def on_closing(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()


if __name__ == "__main__":
    ChatClient()