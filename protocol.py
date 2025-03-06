import socket

class Request:
    def __init__(self):
        self.data = bytearray()
    
    def connection_request(self):
        data = bytearray(4)
        action = 0
        data[0:4] = action.to_bytes(4, 'little')
        return data
    
    def connection_response(self):
        data = bytearray(4)
        action = 0
        data[0:4] = action.to_bytes(4, 'little')
        return data
    
    def announce_request(self, torrent, peerID, downloaded, uploaded, left, event, ip, port):
        data = bytearray(78)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:24] = torrent.encode()
        data[24:44] = peerID.encode()
        data[44:52] = downloaded.to_bytes(8, 'little')
        data[52:60] = uploaded.to_bytes(8, 'little')
        data[60:68] = left.to_bytes(8, 'little')
        data[68:72] = event.to_bytes(4, 'little')
        ip_list = ip.split(".")
        data[72] = (int(ip_list[0])).to_bytes(1, "little")
        data[73] = (int(ip_list[1])).to_bytes(1, "little")
        data[74] = (int(ip_list[2])).to_bytes(1, "little")
        data[75] = (int(ip_list[3])).to_bytes(1, "little")
        data[76:] = port.to_bytes(2, 'little')
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
        action = int.from_bytes(request[0:4], 'little')

        if action == 1:
            interval = int.from_bytes(request[4:12], 'little')
            leechers = int.from_bytes(request[12:16], 'little')
            seeders = int.from_bytes(request[16:], 'little')
            return interval, leechers, seeders

    def tracker_decode(self, request):
        action = int.from_bytes(request[0:4], 'little')

        if action == 1:
            response = {}
            response["torrent"] = request[4:24].decode()
            response["peerID"] = request[24:44].decode()
            response["downloaded"] = int.from_bytes(request[44:52], 'little')
            response["uploaded"] = int.from_bytes(request[52:60])
            response["left"] = int.from_bytes(request[60:68], "little")
            response["event"] = int.from_bytes(request[68:72], "little")
            response["ip"] = request[72]
            response["port"] = int.from_bytes(request[76:], "little")

            return response