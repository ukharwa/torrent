import time
from src.peer import Peer
import hashlib

class Request:
    def __init__(self):
        self.data = bytearray()
    
    def connection_request(self):
        data = bytearray(4)
        action = 0          #connect action
        data[0:4] = action.to_bytes(4, 'little')
        return data
    
    def connection_response(self, connectionID):
        data = bytearray(12)
        action = 0          #connect action
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = connectionID
        return data
    
    #Sends the information about the Peer and their corresponding  to the Tracker
    def announce_request(self, connectionID, file_hash, peerID, downloaded, uploaded, left, event, ip, port):
        data = bytearray(110)
        action = 1                                          #announce action
        data[0:4] = action.to_bytes(4, 'little')            #action 0: connect, 1: announce, 99: error
        data[4:12] = connectionID                           
        data[12:44] = file_hash.encode()                    #hash of the file being shared/recevied
        data[44:76] = peerID.encode()
        data[76:84] = downloaded.to_bytes(8, 'little')      #number of bytes downloaded
        data[84:92] = uploaded.to_bytes(8, 'little')        #number of bytes uploaded
        data[92:100] = left.to_bytes(8, 'little')            #number of bytes left to download
        data[100:104] = event.to_bytes(4, 'little')           #0:none 1:completed 2:stopped
        data[104:108] = ip_to_bytes(ip)                       #peers ip address
        data[108:110] = port.to_bytes(2, 'little')            #connection port
        return data

    def announce_response(self, interval, num_leechers, num_seeders, seeders):#response to the leecher
        data = bytearray(20 + 6*num_seeders)
        action = 1
        data[0:4] = action.to_bytes(4, 'little')
        data[4:12] = interval.to_bytes(8, 'little')
        data[12:16] = num_leechers.to_bytes(4, 'little')        #number of peers leeching
        data[16:20] = num_seeders.to_bytes(4, 'little')         #number of peers seeding
        for i in range(0, len(seeders)):
            data[20+(i * 6): 26+(i*6)] = peer_to_bytes(seeders[i])

        return data
    
    def send_error(self, message):  #send error message
        data = bytearray(259)
        action = 99
        data[0:4] = action.to_bytes(4, 'little')
        data[4:8] = len(message).to_bytes(4, 'little')
        data[8:] = message.encode()
        return data
    
    def client_decode(self, request):   #decodes the request from the client
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        #connect action
        if action == 0:
           response["connectionID"] = request[4:]
           return response
        #announce action
        if action == 1:
            response["interval"] = int.from_bytes(request[4:12], 'little')
            response["num_leechers"] = int.from_bytes(request[12:16], 'little')
            num_seeders  = int.from_bytes(request[16:20], 'little')
            response["num_seeders"] = num_seeders
            seeders = []
            for i in range(num_seeders):
                seeders.append(peer_from_bytes(request[20 + (i*6):26+(i*6)]))
            response["seeders"] = seeders
            
            return response 
        #error action
        if action == 99:
            response["ERROR"] = (request[8:8+int.from_bytes(request[4:8], "little")]).decode()       

        return response

    def tracker_decode(self, request):
        response = {}
        action = int.from_bytes(request[0:4], 'little')

        if action == 1:
            response["connectionID"] = request[4:12]
            response["file_hash"] = request[12:44].decode()
            response["peerID"] = request[44:76].decode()
            response["downloaded"] = int.from_bytes(request[76:84], 'little')
            response["uploaded"] = int.from_bytes(request[84:92])
            response["left"] = int.from_bytes(request[92:100], "little")
            response["event"] = int.from_bytes(request[100:104], "little")
            response["ip"] = ip_from_bytes(request[104:108])
            response["port"] = int.from_bytes(request[108:110], "little")
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

def peer_to_bytes(peer):
    data = bytearray(6)
    data[0:4] = ip_to_bytes(peer.ip)
    data[4:6] = peer.port.to_bytes(2, 'little')
    return data

def peer_from_bytes(data):
    ip = ip_from_bytes(data[0:4])
    port = int.from_bytes(data[4:6], 'little')
    return ip, port

def getpackets(filename, packet_size):
    packets = {}
    with open(filename, "rb") as file:
        while piece := file.read(packet_size):
            data = bytearray(4 + len(piece))
            data[0:4] = len(piece).to_bytes(4, 'little')
            data[4:] = piece 
            packets[hashlib.sha256(piece).hexdigest()] = data 
    return packets

def recv_all(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            break  # Connection closed
        data += packet
    return data
