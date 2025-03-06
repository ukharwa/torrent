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
        data[72:76] = ip.to_bytes(4, 'little')
        data[76:] = port.to_bytes(2, 'little')
        return data

    def announce_response(self, interval, leechers, seeders, peers):
        data = bytearray(20)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = interval.to_bytes(8, 'little')
        data[12:16] = leechers.to_bytes(4, 'little')
        data[12:16] = seeders.to_bytes(4, 'little')