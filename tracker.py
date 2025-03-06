import time
import socket
from peer import Peer
from protocol import *

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('196.42.75.61', 6969))

peers = {}
connections = {} 

protocol = Request()

while True:
    data, addr = tracker.recvfrom(1024)
    action = int.from_bytes(data[0:4], "little")
    print("Action request: " + str(action))

    if action == 0:
        print("Connection request from " + addr[0] +  " receivied...")
        connectionID = get_connectionID(addr[0])
        connections["connectionID"] = time.time()
        tracker.sendto(protocol.connection_response(connectionID), addr)

    if action == 1:
        response = protocol.tracker_decode(data)
        if response["connectionID"] in connections:
            peers[response["peerID"]] = peer_from_announce(response)
            tracker.sendto(protocol.announce_response(300, 20, 100), addr)


