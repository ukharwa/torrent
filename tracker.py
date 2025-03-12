import time
import socket
from src.protocol import *

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('196.42.74.94', 6969))

files = {}
connections = {}
peers = {}

protocol = Request()
print("Tracker online")

def await_message():
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
                file = response["file_hash"]
                peerID = response["peerID"]

                if response["event"] == 0: # update
                    peers[peerID][file] = peer_from_announce(response)
                
                if response["event"] == 1: #started
                    if peerID not in peers:
                        peers[peerID] = dict(file = peer_from_announce(response))
                    else:
                        peers[peerID][file] = peer_from_announce(response)

                    
                    if file not in files:
                        files[file] = dict(seeders = set(), leechers = set())
                    
                    if response["left"] > 0:
                        files[file]["leechers"].add(peerID)
                    else:
                        files[file]["seeders"].add(peerID)
                    
                    seeders = []
                    for s in file[files]["seeders"]:
                        seeders.append(protocol.peer_to_bytes(peers[s][file]))
                    tracker.sendto(protocol.announce_response(90, len(files[file]["seeders"], seeders)))

                elif response["event"] == 2: #stopped
                    if response["left"] > 0:
                        files[file]["leechers"].remove(peerID)
                    else:
                        files[file]["seeders"].remove(peerID)
                    
                    peers[peerID].pop(file)
                    if len(peers[peerID]) == 0:
                        peers.pop(peerID)

            else:
                print("Invalid connectionID received")
                tracker.sendto(protocol.send_error("Invalid connectionID"), addr)

def cleanup():
    for conn, t in connections:
        if (time.time()).__trunc__() - t > 900:
            connections.pop(conn)

    for peer in peers:
        for file in peer.values():
            if (time.time()).__trunc__() - file.announce_time() > 300:
                if file.left > 0:
                    files[file]["leechers"].remove(peer)
                else:
                    files[file]["seeders"].remove(peer)
                    
                peers[peer].pop(file)
                if len(peers[peer]) == 0:
                    peers.pop(peer)

