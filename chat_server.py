import socket
import threading
import json
import datetime
import os

HOST = '127.0.0.1'
PORT = 55555
HTTP_PORT = 8080
LOG_FILE = 'chat_log.txt'

clients = {}


def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except:
        pass


def broadcast_user_list():
    user_list = list(clients.values())
    packet = {"type": "USER_LIST", "content": user_list}
    json_data = json.dumps(packet).encode('utf-8')
    for sock in clients:
        try:
            sock.send(json_data)
        except:
            pass


def broadcast_message(message_dict):
    json_data = json.dumps(message_dict).encode('utf-8')
    for sock in clients:
        try:
            sock.send(json_data)
        except:
            pass


def send_private_message(target_nickname, message_dict):
    json_data = json.dumps(message_dict).encode('utf-8')
    for sock, nick in clients.items():
        if nick == target_nickname:
            try:
                sock.send(json_data)
                return True
            except:
                return False
    return False


def handle_http_client(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')

        log_content = ""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log_content = f.read()

        html_response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<html>
<head><title>Chat Logs</title></head>
<body>
    <h1>Server Logs</h1>
    <pre>{log_content}</pre>
    <p><i>Refresh the page to see new logs.</i></p>
</body>
</html>
"""
        client_socket.send(html_response.encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()


def start_http_server():
    http_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_server.bind((HOST, HTTP_PORT))
    http_server.listen()
    print(f"Web Server started on http://{HOST}:{HTTP_PORT}")

    while True:
        client_sock, addr = http_server.accept()
        threading.Thread(target=handle_http_client, args=(client_sock,)).start()


def handle_client(client_socket, address):
    nickname = ""
    try:
        buffer = client_socket.recv(1024).decode('utf-8')
        if not buffer:
            client_socket.close()
            return

        data = json.loads(buffer)
        requested_nickname = data.get("content")

        if requested_nickname in clients.values():
            nickname = requested_nickname + str(len(clients))
        else:
            nickname = requested_nickname

        clients[client_socket] = nickname

        log_event(f"CONNECTION: {nickname} connected from {address}")

        join_msg = {
            "type": "SYSTEM",
            "content": f"{nickname} has joined the chat.",
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        }
        broadcast_message(join_msg)
        broadcast_user_list()

        while True:
            buffer = client_socket.recv(1024)
            if not buffer:
                break

            msg_str = buffer.decode('utf-8')
            msg_data = json.loads(msg_str)

            timestamp = datetime.datetime.now().strftime("%H:%M")
            content = msg_data.get("content")
            msg_type = msg_data.get("type")
            target = msg_data.get("target")

            if msg_type == "PUBLIC":
                packet = {"type": "PUBLIC", "sender": nickname, "content": content, "timestamp": timestamp}
                log_event(f"PUBLIC ({nickname}): {content}")
                broadcast_message(packet)

            elif msg_type == "PRIVATE":
                packet = {"type": "PRIVATE", "sender": nickname, "content": content, "timestamp": timestamp}
                log_event(f"PRIVATE ({nickname} -> {target}): {content}")
                if send_private_message(target, packet):
                    client_socket.send(json.dumps(packet).encode('utf-8'))

    except:
        pass
    finally:
        if client_socket in clients:
            del clients[client_socket]
            log_event(f"DISCONNECT: {nickname} disconnected")
            leave_msg = {"type": "SYSTEM", "content": f"{nickname} has left.",
                         "timestamp": datetime.datetime.now().strftime("%H:%M")}
            broadcast_message(leave_msg)
            broadcast_user_list()
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Chat Server started on {HOST}:{PORT}")

    web_thread = threading.Thread(target=start_http_server)
    web_thread.daemon = True
    web_thread.start()

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()


if __name__ == "__main__":
    start_server()