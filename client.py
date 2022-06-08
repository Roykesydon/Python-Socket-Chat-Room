import socket
import sys
import threading

from utils.config import read_config
from utils.message import recv, send

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

config = read_config()

server_host = config["server_ip"]
server_port = int(config["server_port"])

stop_thread = False

threads = []


def connect_to_server():
    try:
        client.connect((server_host, server_port))
    except Exception as error:
        print(error)
        sys.exit()


def receive():
    global stop_thread, config
    while not stop_thread:
        try:
            message = recv(client, config)
            if message == "":
                print("Server Error")
                stop_thread = True
                break
            print(message)

        except Exception as error:
            print(error)
            client.close()
            break


def send_to_server():
    global stop_thread
    while not stop_thread:
        try:
            message = input()
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            send(client, message, config)
        except Exception as error:
            print(error)
            client.close()
            break


connect_to_server()

receive_thread = threading.Thread(target=receive)
threads.append(receive_thread)
receive_thread.start()

send_thread = threading.Thread(target=send_to_server)
threads.append(send_thread)
send_thread.start()
