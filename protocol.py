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
        data[4:] = connectionID
        return data
    
    def announce_request(self, connectionID, torrent, peerID, downloaded, uploaded, left, event, ip, port):
        data = bytearray(98)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:24] = connectionID.encode()
        data[24:44] = torrent.encode()
        data[44:64] = peerID.encode()
        data[64:72] = downloaded.to_bytes(8, 'little')
        data[72:80] = uploaded.to_bytes(8, 'little')
        data[80:88] = left.to_bytes(8, 'little')
        data[88:92] = event.to_bytes(4, 'little')
        data[92:96] = ip_to_bytes(ip)
        data[96:] = port.to_bytes(2, 'little')
        return data

    def announce_response(self, interval, leechers, seeders):
        data = bytearray(20)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = interval.to_bytes(8, 'little')
        data[12:16] = leechers.to_bytes(4, 'little')
        data[16:] = seeders.to_bytes(4, 'little')
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
            response["seeders"] = int.from_bytes(request[16:], 'little')
            return response

        return response

    def tracker_decode(self, request):
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        if action == 1:
            response["connectionID"] = request[4:24]
            response["torrent"] = request[24:44].decode()
            response["peerID"] = request[44:64].decode()
            response["downloaded"] = int.from_bytes(request[64:72], 'little')
            response["uploaded"] = int.from_bytes(request[72:80])
            response["left"] = int.from_bytes(request[80:88], "little")
            response["event"] = int.from_bytes(request[88:92], "little")
            response["ip"] = ip_from_bytes(request[92:96])
            response["port"] = int.from_bytes(request[96:], "little")
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
    ip = [str(data[92]), str(data[93]), str(data[94]), str(data[95])]
    return ".".join(ip)


def get_connectionID(ip):
    connectionID = bytearray(8)
    connectionID[0:4] = ip_to_bytes(ip)
    connectionID[4:] = int.to_bytes((time.time()).__trunc__())
    return connectionID

def peer_from_announce(response):
    return Peer(response["ip"], response["port"], response["downloaded"], response["uploaded"], response["left"], response["event"], (time.time()).__trunc__())
