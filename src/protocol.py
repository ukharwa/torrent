
import time
import hashlib
from src.peer import Peer

class Protocol:

    def __init__(self):
        self.data = bytearray()

    def connection_request(self) -> bytearray: # Create a connection request message.
        data = bytearray(4)
        action = 0  # Connect action
        data[0:4] = action.to_bytes(4, 'little')
        return data

    def connection_response(self, connectionID: bytearray) -> bytearray: # Create a connection response message including the connection ID.
        data = bytearray(12)
        action = 0  # Connect action
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = connectionID
        return data

    def announce_request(self, connectionID, file_hash, peerID, downloaded, uploaded, left, event, ip, port): # Create an announcement request containing peer and file information.
        data = bytearray(110)
        action = 1  # Announce action
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = connectionID
        data[12:44] = file_hash.encode()             # file hash
        data[44:76] = peerID.encode()                  # peer identifier
        data[76:84] = downloaded.to_bytes(8, 'little') # bytes downloaded
        data[84:92] = uploaded.to_bytes(8, 'little')   # bytes uploaded
        data[92:100] = left.to_bytes(8, 'little')      # bytes left
        data[100:104] = event.to_bytes(4, 'little')      # event code (0: none, 1: completed, 2: stopped)
        data[104:108] = ip_to_bytes(ip)                # peer IP address
        data[108:110] = port.to_bytes(2, 'little')       # connection port
        return data

    def announce_response(self, interval, num_leechers, seeders): # Create an announcement response to be sent to a leecher.
        num_seeders = len(seeders)
        data = bytearray(20 + 6 * num_seeders)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = interval.to_bytes(8, 'little')
        data[12:16] = num_leechers.to_bytes(4, 'little')  # number of leechers
        data[16:20] = num_seeders.to_bytes(4, 'little')   # number of seeders

        for i, peer in enumerate(seeders):
            data[20 + (i * 6): 26 + (i * 6)] = peer_to_bytes(peer)

        return data

    def send_error(self, message): # Create an error message.
        data = bytearray(259)
        action = 99
        data[0:4] = action.to_bytes(4, 'little')
        data[4:8] = len(message).to_bytes(4, 'little')
        data[8:] = message.encode()
        return data

    def client_decode(self, request): # Decode a client request.
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        # Connect action
        if action == 0:
            response["connectionID"] = request[4:]
            return response

        # Announce action
        if action == 1:
            response["interval"] = int.from_bytes(request[4:12], 'little')
            response["num_leechers"] = int.from_bytes(request[12:16], 'little')
            num_seeders = int.from_bytes(request[16:20], 'little')
            response["num_seeders"] = num_seeders
            seeders = []
            for i in range(num_seeders):
                seeders.append(peer_from_bytes(request[20 + (i * 6):26 + (i * 6)]))
            response["seeders"] = seeders
            return response

        # Error action
        if action == 99:
            msg_length = int.from_bytes(request[4:8], "little")
            response["ERROR"] = request[8:8 + msg_length].decode()

        return response

    def tracker_decode(self, request): # Decode a tracker request.
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        if action == 1:
            response["connectionID"] = request[4:12]
            response["file_hash"] = request[12:44].decode()
            response["peerID"] = request[44:76].decode()
            response["downloaded"] = int.from_bytes(request[76:84], 'little')
            response["uploaded"] = int.from_bytes(request[84:92], 'little')
            response["left"] = int.from_bytes(request[92:100], "little")
            response["event"] = int.from_bytes(request[100:104], "little")
            response["ip"] = ip_from_bytes(request[104:108])
            response["port"] = int.from_bytes(request[108:110], "little")
            return response

        return response


def ip_to_bytes(ip): # Convert a dotted IP string to a 4-byte array.
    ip_list = ip.split(".")
    data = bytearray(int(octet) for octet in ip_list)
    return data


def ip_from_bytes(data): # Convert a 4-byte array to a dotted IP string.
    return ".".join(str(b) for b in data[0:4])


def get_connectionID(ip): # Create a connection ID using the IP and current timestamp.
    connectionID = bytearray(8)
    connectionID[0:4] = ip_to_bytes(ip)
    timestamp = int(time.time())
    connectionID[4:] = timestamp.to_bytes(4, 'little')
    return connectionID


def decode_connectionID(conID): # Decode the connection ID to retrieve the originating IP and timestamp.
    ip_str = ip_from_bytes(conID[0:4])
    timestamp = int.from_bytes(conID[4:], 'little')
    return f"{ip_str}{timestamp}"


def peer_from_announce(response): # Create a Peer object from an announcement response.
    return Peer(
        response["ip"],
        response["port"],
        response["downloaded"],
        response["uploaded"],
        response["left"],
        response["event"],
        int(time.time())
    )


def peer_to_bytes(peer): # Convert a Peer (or an IP/port tuple) to a 6-byte representation.
    if isinstance(peer, Peer):
        ip = peer.ip
        port = peer.port
    else:
        ip, port = peer
    data = bytearray(6)
    data[0:4] = ip_to_bytes(ip)
    data[4:6] = port.to_bytes(2, 'little')
    return data


def peer_from_bytes(data): # Convert a 6-byte array into an IP string and port tuple.
    ip = ip_from_bytes(data[0:4])
    port = int.from_bytes(data[4:6], 'little')
    return ip, port


def getpackets(filename, packet_size):
    # Read a file and break it into packets of a given size.
    # Each packet is keyed by its SHA-256 hash.
    packets = []
    i = 0
    with open(filename, "rb") as file:
        while (piece := file.read(packet_size)):
            data = bytearray(8 + len(piece))
            data[0:4] = len(piece).to_bytes(4, 'little')
            data[4:8] = i.to_bytes(4, 'little')
            data[8:] = piece
            packets[i] = data
            i += 1
    return packets


def recv_all(sock, size): # Receive exactly 'size' bytes from the socket.
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            break  # Connection closed
        data += packet
    return data

