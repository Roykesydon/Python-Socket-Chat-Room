import unittest
from unittest.mock import patch
import socket

from src.utils import message
from src.utils.config import read_config


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.config = read_config()

    def tearDown(self):
        self.args = None

    @patch("socket.socket")
    def test_send(self, mock_socket):
        # Ignore whether successfully send message or not
        mock_socket.return_value.send.return_value = None

        _message = "testing"
        _byte_message = _message.encode("utf-8")
        header = (0).to_bytes(1, "big") + (len(_byte_message)).to_bytes(
            int(self.config["message_len_bytes"]), "big"
        )

        result = message.send(socket.socket(), _message, self.config)
        self.assertEqual(result, header + _byte_message)

    @patch("socket.socket")
    def test_recv(self, mock_socket):

        _message = "testingtesting"
        _byte_message = _message.encode("utf-8")
        header = (0).to_bytes(1, "big") + (len(_byte_message)).to_bytes(
            int(self.config["message_len_bytes"]), "big"
        )
        package = header + _byte_message

        mock_socket.return_value.recv.side_effect = [package[:1], package[1:5], package[5:]]
        result = message.recv(socket.socket(), self.config, [b""])
        self.assertEqual(result, _message)

    def test_can_get_complete_message(self):
        test_cases = [
            (3, ["testing"], True),
            (3, ["testing"], False),
            (3, ["testing", "testing"], True),
        ]

        for test_case in test_cases:
            message_len_bytes, messages, complete_flag = test_case
            byte_messages = [message.encode("utf-8") for message in messages]

            packages = b""
            for index, byte_message in enumerate(byte_messages):
                not_end_package = 0 if index == len(byte_messages) - 1 else 1
                header = (not_end_package).to_bytes(1, "big") + (
                    len(byte_message)
                ).to_bytes(message_len_bytes, "big")

                if not complete_flag and index == len(byte_messages) - 1:
                    packages += header + byte_message[:-1]
                else:
                    packages += header + byte_message

            result = message.can_get_complete_message(message_len_bytes, packages)

            self.assertEqual(result, complete_flag)
