import time
import socket
from protocol import *

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('localhost', 6969))

peers = {}
connections = {} 

protocol = Request()
print("Tracker online")

while True:
    data, addr = tracker.recvfrom(1024)
    action = int.from_bytes(data[0:4], "little")

    if action == 0:
        print("Connection request from " + addr[0] +  " receivied...")
        connectionID = get_connectionID(addr[0])
        connections[decode_connectionID(connectionID)] = time.time()
        tracker.sendto(protocol.connection_response(connectionID), addr)

    if action == 1:
        print("Announcement received from " + addr[0])
        response = protocol.tracker_decode(data)
        connectionID = response["connectionID"]
        if decode_connectionID(connectionID) in connections:
            print("connectionID found")
            peers[response["peerID"]] = peer_from_announce(response)
            print("Peer " + response["peerID"] + " connected")
            tracker.sendto(protocol.announce_response(300, 20, 100), addr)
        else:
            print("Invalid connectionID received")
            tracker.sendto(protocol.send_error("Invalid connectionID"), addr)


