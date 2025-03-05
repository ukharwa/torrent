import socket

class Protocol:
    def __init__(self):
        self.data = bytearray(260)

    def post(self, socket, ip, port):
        socket.sendto(self.data, (ip, port))
    
    def sendMessage(self, message):
        self.data[0] = 0
        self.data[1:5] = len(message).to_bytes(4, 'little')
        self.data[5:] = message.encode()

    def sendSeeder(self, ip, port):
        self.data[0] = 1
        self.data[1:5] = len(ip).to_bytes(4, "little")
        self.data[5:9] = port.to_bytes(4, "little")
        self.data[9:] = ip.encode()

    def receive(self, data):
        type = data[0]
        length = int.from_bytes(data[1:5], 'little')

        if type == 0:
            message = data[9:9+length].decode()
            print(message)
            return
        
        if type == 1:
            port = int.from_bytes(data[5:9], "little")
            ip = data[9:9+length].decode()
            return ip, port