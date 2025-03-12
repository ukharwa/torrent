import time
import socket
import threading
from src.protocol import *

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker_ip = socket.gethostbyname(socket.gethostname())
tracker_port = 6969
tracker.bind((tracker_ip, tracker_port))

files = {}
connections = {}
peers = {}

protocol = Request()
print("Tracker online")
print(tracker_ip + " : " + "listening on port "  + str(tracker_port))

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
                        peers[peerID] = dict()
                        peers[peerID][file] = peer_from_announce(response)
                    else:
                        peers[peerID][file] = peer_from_announce(response)

                    
                    if file not in files:
                        files[file] = dict(seeders = set(), leechers = set())
                    
                    if response["left"] > 0:
                        files[file]["leechers"].add(peerID)
                    else:
                        files[file]["seeders"].add(peerID)
                    
                    print(peers)
                    seeders = []
                    for s in files[file]["seeders"]:
                        seeders.append(peers[s][file])
                    tracker.sendto(protocol.announce_response(90, len(files[file]["leechers"]), seeders), addr)

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
    while True:
        time.sleep(60)  # Run cleanup every 60 seconds
        print("Running cleanup...")
        
        to_remove = []
        for conn, t in connections.items():
            if int(time.time()) - t > 900:
                to_remove.append(conn)

        for conn in to_remove:
            connections.pop(conn, None)

        peer_remove = []
        for peer, files_dict in peers.items():
            file_remove = []
            for file, peer_info in files_dict.items():
                if int(time.time()) - peer_info.announce_time() > 300:
                    file_remove.append(file)

            for file in file_remove:
                if peers[peer][file].left > 0:
                    files[file]["leechers"].remove(peer)
                else:
                    files[file]["seeders"].remove(peer)

                peers[peer].pop(file, None)
                
            if not peers[peer]:
                peer_remove.append(peer)

        for peer in peer_remove:
            peers.pop(peer, None)

        print("Cleanup complete.")

# Start both functions in separate threads
thread1 = threading.Thread(target=await_message, daemon=True)
thread2 = threading.Thread(target=cleanup, daemon=True)

thread1.start()
thread2.start()

# Keep the main program alive
thread1.join()
thread2.join()
