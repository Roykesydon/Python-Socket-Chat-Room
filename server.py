import socket
import threading
import time
from typing import Callable

from utils.config import read_config
from utils.message import recv, send

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

config = read_config()
lock = threading.Lock()

host = config["server_ip"]
# host = "127.0.0.1"
port = int(config["server_port"])

server.bind((host, port))
server.listen()


clients = []
nickname_address_list = []


def synchronized(func: Callable) -> Callable:
    def wrap(*args, **kwargs):
        lock.acquire()
        func(*args, **kwargs)
        lock.release()

    return wrap


@synchronized
def close_connection_with_client(client: socket.socket, nickname_address: str) -> None:
    if client in clients:
        clients.remove(client)
        client.close()

    if nickname_address is not None:
        nickname, address = (
            "-".join(nickname_address.split("-")[:-1]),
            nickname_address.split("-")[-1],
        )

        print(f"Close connection with {address}")
        nickname_address_list.remove(nickname_address)
        broadcast(f"{nickname} lefted")


def broadcast(message: str) -> None:
    global config

    for client in clients.copy():
        try:
            send(client, message, config)
        except Exception as error:
            print(error)
            index = clients.index(client)
            nickname_address = nickname_address_list[index]
            close_connection_with_client(client, nickname_address)


def handle(client: socket.socket, address: str):
    global config
    nickname_address = None
    buffer=[b""]

    try:
        send(client, "Input your nick name:", config)

        nickname = recv(client, config, buffer)

        nickname_address = f"{nickname}-{address}:{port}"
        nickname_address_list.append(nickname_address)
        clients.append(client)
        print(f"Address: {str(address)}, nickname: {nickname}")

        send(client, "Connected to server!", config)
        broadcast(f"{nickname} joined")

        while True:
            message = recv(client, config, buffer)
            if message == "":
                close_connection_with_client(client, nickname_address)
                break
            broadcast(f"{nickname}: {message}")
    except Exception as error:
        print(error)
        close_connection_with_client(client, nickname_address)


def main():

    while True:
        try:
            client, (ip, port) = server.accept()
            address = f"{ip}:{port}"
            print(f"Connected with {address}")

            thread = threading.Thread(target=handle, args=(client, address))
            thread.daemon = True
            thread.start()
        except Exception as error:
            print(error)
            break
    server.close()


if __name__ == "__main__":
    main()
