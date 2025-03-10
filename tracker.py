import time
import socket
from protocol import *

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('localhost', 6969))

files = {
}
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
            peer = peer_from_announce(response)
            file = response["file_hash"]

            if response["left"] > 0:
                if file in files:
                    files[file]["leechers"][response["peerID"]] = peer
                else:
                    tracker.sendto(protocol.send_error("No seeders for this file"), addr)
                    continue
            else:
                if file in files:
                     files[file]["seeders"][response["peerID"]] = peer
                else:
                    files[file] = dict(seeders = {response["peerID"] : peer}, leechers = {})

            print("Peer " + response["peerID"] + " connected")
            tracker.sendto(protocol.announce_response(300, len(files[file]["leechers"]), len(files[file]["seeders"]), list(files[file]["seeders"].values())), addr)

        else:
            print("Invalid connectionID received")
            tracker.sendto(protocol.send_error("Invalid connectionID"), addr)


