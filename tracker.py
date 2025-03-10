import time
import socket
from protocol import *

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('196.42.75.186', 6969))

files = {
}
connections = {} 

protocol = Request()
print("Tracker online")

while True:
    print(files)
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
            peer = peer_from_announce(response)
            if response["left"] > 0:
                files[response["file_hash"]]["leechers"][response["peerID"]] = peer
            else:
                if response["file_hash"] in  files:
                     files[response["file_hash"]]["seeders"][response["peerID"]] = peer
                else:
                    files[response["file_hash"]] = dict(seeders = {response["peerID"] : peer}, leechers = {})
            print("Peer " + response["peerID"] + " connected")
            tracker.sendto(protocol.announce_response(300, 20, 100), addr)
        else:
            print("Invalid connectionID received")
            tracker.sendto(protocol.send_error("Invalid connectionID"), addr)


