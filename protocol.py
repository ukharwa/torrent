import time
from peer import Peer

class Request:
    def __init__(self):
        self.data = bytearray()
    
    def connection_request(self):
        data = bytearray(4)
        action = 0
        data[0:4] = action.to_bytes(4, 'little')
        return data
    
    def connection_response(self, connectionID):
        data = bytearray(12)
        action = 0
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = connectionID
        return data
    
    def announce_request(self, connectionID, torrent, peerID, downloaded, uploaded, left, event, ip, port):
        data = bytearray(86)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = connectionID
        data[12:32] = torrent.encode()
        data[32:52] = peerID.encode()
        data[52:60] = downloaded.to_bytes(8, 'little')
        data[60:68] = uploaded.to_bytes(8, 'little')
        data[68:76] = left.to_bytes(8, 'little')
        data[76:80] = event.to_bytes(4, 'little')
        data[80:84] = ip_to_bytes(ip)
        data[84:86] = port.to_bytes(2, 'little')
        return data

    def announce_response(self, interval, leechers, seeders):
        data = bytearray(20)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = interval.to_bytes(8, 'little')
        data[12:16] = leechers.to_bytes(4, 'little')
        data[16:20] = seeders.to_bytes(4, 'little')
        return data
    
    def send_error(self, message):
        data = bytearray(259)
        action = 99
        data[0:4] = action.to_bytes(4, 'little')
        data[4:8] = len(message).to_bytes(4, 'little')
        data[8:] = message.encode()
        return data
    
    def client_decode(self, request):
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        if action == 0:
           response["connectionID"] = request[4:]
           return response

        if action == 1:
            response["interval"] = int.from_bytes(request[4:12], 'little')
            response["leechers"] = int.from_bytes(request[12:16], 'little')
            response["seeders"] = int.from_bytes(request[16:20], 'little')
            return response

        if action == 99:
            response["ERROR"] = (request[8:8+int.from_bytes(request[4:8], "little")]).decode()       

        return response

    def tracker_decode(self, request):
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        if action == 1:
            response["connectionID"] = request[4:12]
            response["torrent"] = request[12:32].decode()
            response["peerID"] = request[32:52].decode()
            response["downloaded"] = int.from_bytes(request[52:60], 'little')
            response["uploaded"] = int.from_bytes(request[60:68])
            response["left"] = int.from_bytes(request[68:76], "little")
            response["event"] = int.from_bytes(request[76:80], "little")
            response["ip"] = ip_from_bytes(request[80:84])
            response["port"] = int.from_bytes(request[84:86], "little")
            return response

        return response

def ip_to_bytes(ip):
    ip_list = ip.split(".")
    data = bytearray()
    data.append(int(ip_list[0]))
    data.append(int(ip_list[1]))
    data.append(int(ip_list[2]))
    data.append(int(ip_list[3]))
    return data

def ip_from_bytes(data):
    ip = [str(int.from_bytes(data[0:1])), str(int.from_bytes(data[1:2])), str(int.from_bytes(data[2:3])), str(int.from_bytes(data[3:]))]
    return ".".join(ip)


def get_connectionID(ip):
    connectionID = bytearray(8)
    connectionID[0:4] = ip_to_bytes(ip)
    connectionID[4:] = ((time.time()).__trunc__()).to_bytes(4, 'little')
    return connectionID

def decode_connectionID(conID):
    ip = ip_from_bytes(conID[0:4])
    time = int.from_bytes(conID[4:])
    return ip  + str(time)

def peer_from_announce(response):
    return Peer(response["ip"], response["port"], response["downloaded"], response["uploaded"], response["left"], response["event"], (time.time()).__trunc__())
