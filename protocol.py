import socket

class Protocol:
    def __init__(self, socket=None):
        self.data = bytearray(260)
        self.socket = socket

    def post(self, ip, port):
        self.socket.sendto(self.data, (ip, port))
        self.data = bytearray(260)
    
    def sendMessage(self, message, ip, port):
        self.data[0] = 0
        self.data[1:5] = len(message).to_bytes(4, 'little')
        self.data[5:] = message.encode()
        self.post(ip, port)

    def sendIP(self, Mip, Mport, ip, port):
        self.data[0] = 1
        self.data[1:5] = len(Mip).to_bytes(4, "little")
        self.data[5:9] = Mport.to_bytes(4, "little")
        self.data[9:] = Mip.encode()
        self.post(ip, port)

    def receive(self, data):
        type = data[0]
        length = int.from_bytes(data[1:5], 'little')

        if type == 0:
            message = data[5:9+length].decode()
            print(message)
            return type, message
        
        if type == 1:
            port = int.from_bytes(data[5:9], "little")
            ip = data[9:9+length].decode()
            return type, (ip, port)
        
        if type == 2:
            file = data[5:9+length].decode()
            return type, file