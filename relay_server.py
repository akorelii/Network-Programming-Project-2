import socket
import threading
import json

MAIN_SERVER_HOST = '127.0.0.1'
MAIN_SERVER_PORT = 55555

RELAY_HOST = '127.0.0.1'
RELAY_PORT = 55556


def handle_server_to_client(server_socket, client_socket):
    try:
        while True:
            data = server_socket.recv(1024)
            if not data:
                break
            client_socket.send(data)
    except:
        pass
    finally:
        server_socket.close()
        client_socket.close()


def handle_client_to_server(client_socket, server_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            server_socket.send(data)
    except:
        pass
    finally:
        client_socket.close()
        server_socket.close()


def handle_relay(client_socket):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect((MAIN_SERVER_HOST, MAIN_SERVER_PORT))

        initial_data = client_socket.recv(1024).decode('utf-8')
        if not initial_data:
            return

        json_data = json.loads(initial_data)
        original_nickname = json_data.get("content")

        new_nickname = "*" + original_nickname
        json_data["content"] = new_nickname

        print(f"Relaying connection: {original_nickname} -> {new_nickname}")

        server_socket.send(json.dumps(json_data).encode('utf-8'))

        t1 = threading.Thread(target=handle_server_to_client, args=(server_socket, client_socket))
        t2 = threading.Thread(target=handle_client_to_server, args=(client_socket, server_socket))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    except Exception as e:
        print(f"Relay error: {e}")
        client_socket.close()
        server_socket.close()


def start_relay():
    relay = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    relay.bind((RELAY_HOST, RELAY_PORT))
    relay.listen()

    print(f"Relay Server started on {RELAY_HOST}:{RELAY_PORT}")
    print(f"Forwarding to Main Server on {MAIN_SERVER_HOST}:{MAIN_SERVER_PORT}")

    while True:
        client_sock, addr = relay.accept()
        thread = threading.Thread(target=handle_relay, args=(client_sock,))
        thread.start()


if __name__ == "__main__":
    start_relay()