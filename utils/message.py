import socket
import struct
from typing import Tuple, List


def send(_socket: socket.socket, message: str, config: dict) -> None:
    message_len_bytes = int(config["message_len_bytes"])
    byte_message = message.encode("utf-8")
    packages = []
    while len(byte_message) != 0:
        if len(byte_message) > (1 << (message_len_bytes * 3)) - 1:
            packages.append(
                (1).to_bytes(1, "big")
                + ((1 << (message_len_bytes * 3)) - 1).to_bytes(
                    message_len_bytes, "big"
                )
                + byte_message[: (1 << (message_len_bytes * 3)) - 1]
            )
            byte_message = byte_message[(1 << (message_len_bytes * 3)) - 1 :]
        elif len(byte_message) <= (1 << (message_len_bytes * 3)) - 1:
            packages.append(
                (0).to_bytes(1, "big")
                + (len(byte_message)).to_bytes(message_len_bytes, "big")
                + byte_message
            )
            byte_message = ""
    for package in packages:
        _socket.send(package)


def can_get_complete_message(message_len_bytes: int, message_buffer: bytes) -> bool:
    base = 0
    while True:
        # Not even enough to get package info
        if len(message_buffer[base:]) < 1 + message_len_bytes:
            return False

        have_next_connected_package = bool(
            int.from_bytes(message_buffer[base : base + 1], "big")
        )
        package_len = int.from_bytes(
            message_buffer[base + 1 : base + 1 + message_len_bytes], "big"
        )

        # There's less information than there should be
        if len(message_buffer[base + 1 + message_len_bytes :]) < package_len:
            return False

        # This is the last package
        if not have_next_connected_package:
            return True
        base += message_len_bytes + 1 + package_len


def recv(client: socket.socket, config: dict, buffer: List[bytes]) -> str:
    message_buffer = buffer[0]
    message_len_bytes = int(config["message_len_bytes"])

    while not can_get_complete_message(message_len_bytes, message_buffer):
        package = client.recv(1024)
        if package == b"":
            raise Exception

        message_buffer += package

    message_len_bytes = int(config["message_len_bytes"])

    byte_complete_message = b""
    while True:
        have_next_connected_package = bool(int.from_bytes(message_buffer[:1], "big"))
        package_len = int.from_bytes(message_buffer[1 : 1 + message_len_bytes], "big")

        byte_complete_message += message_buffer[
            1 + message_len_bytes : 1 + message_len_bytes + package_len
        ]

        message_buffer = message_buffer[1 + message_len_bytes + package_len :]

        # This is the last package
        if not have_next_connected_package:
            buffer[0] = message_buffer
            return byte_complete_message.decode("utf-8")


if __name__ == "__main__":
    send(None, "helloworld")
    send(None, "床前明月光")
    send(None, "給我一個bit")
    bytes_int = ((1 << (24 * 3)) - 1).to_bytes(3, "big")
    print(bytes_int)
    print((1 << (24 * 3)) - 1)
    print(int.from_bytes(bytes_int, "big"))
