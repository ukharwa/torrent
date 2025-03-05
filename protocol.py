import socket

class Message:
    def __init__(self, type, content):
        self.data = bytearray(260)
        self.data[0] = type
        self.data[1:5] = len(content).to_bytes(4, 'little')
        self.data[5:] = content

    def send(self, socket, ip, port):
        socket.send