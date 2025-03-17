import time
import socket
import threading
import logging
from src.protocol import *

#configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Tracker:
    def __init__(self, ip="localhost", port=9999):

        # Initialize tracker socket
        self.tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tracker_ip = socket.gethostbyname(socket.gethostname()) if ip == "auto" else ip
        self.tracker_port = port
        self.tracker.bind((self.tracker_ip, self.tracker_port))

        # Shared data structures with a lock for thread safety
        self.files = {}       # {file_hash: {"seeders": set(), "leechers": set()}}
        self.connections = {} # {connectionID: timestamp}
        self.peers = {}       # {peerID: {file_hash: peer_info}}

        self.protocol = Protocol() # Initializes object for formatting messages
        self.lock = threading.Lock() # Ensures thread safety when accessing shared resources

        logging.info(f"Tracker {self.tracker_ip} online. Listening on port {self.tracker_port}")


    def await_message(self): # Listens for incoming messages to process
        while True:
            try:
                data, addr = self.tracker.recvfrom(1024)
                action = int.from_bytes(data[0:4], "little")

                if action == 0:
                    self.handle_connection_request(addr)
                elif action == 1:
                    self.handle_announcement(data, addr)
                else:
                    logging.warning(f"Received unknown action {action} from {addr}")

            except Exception as e:
                logging.error(f"Error in await_message: {e}")


    def handle_connection_request(self, addr): # processes connection requests
        logging.info(f"Connection request from {addr[0]} received...")
        connectionID = get_connectionID(addr[0])
        with self.lock:
            self.connections[decode_connectionID(connectionID)] = time.time()
        self.tracker.sendto(self.protocol.connection_response(connectionID), addr)


    def handle_announcement(self, data, addr): # processes announcements
        logging.info(f"Announcement received from {addr[0]}")
        response = self.protocol.tracker_decode(data)
        connectionID = response["connectionID"]

        with self.lock:
            if decode_connectionID(connectionID) not in self.connections:
                logging.warning(f"Invalid connectionID from {addr}")
                self.tracker.sendto(self.protocol.send_error("Invalid connectionID"), addr)
                return
            
            logging.info("Valid connectionID found")
            file_hash = response["file_hash"]
            peerID = response["peerID"]
            event = response["event"]

            if event == 0:  # peer update
                if peerID in self.peers:
                    self.peers[peerID][file_hash] = peer_from_announce(response)

            elif event == 1:  # peer started
                if peerID not in self.peers:
                    self.peers[peerID] = {}
                self.peers[peerID][file_hash] = peer_from_announce(response)

                if file_hash not in self.files:
                    self.files[file_hash] = {"seeders": set(), "leechers": set()}

                if response["left"] > 0:
                    self.files[file_hash]["leechers"].add(peerID)
                else:
                    self.files[file_hash]["seeders"].add(peerID)

                logging.info(f"Updated peers: {self.peers}")

                seeders = [self.peers[s][file_hash] for s in self.files[file_hash]["seeders"]]
                self.tracker.sendto(self.protocol.announce_response(90, len(self.files[file_hash]["leechers"]), seeders), addr)

            elif event == 2:  # peer stopped
                if peerID in self.peers and file_hash in self.peers[peerID]:
                    if response["left"] > 0:
                        self.files[file_hash]["leechers"].discard(peerID)
                    else:
                        self.files[file_hash]["seeders"].discard(peerID)

                    self.peers[peerID].pop(file_hash, None)

                    if not self.peers[peerID]:
                        del self.peers[peerID]


    def cleanup(self): # clean up old connectionIDs and inactive peers
        while True:
            time.sleep(60)  # run cleanup every 60 seconds
            logging.info("Running cleanup...")

            with self.lock:
                # remove old connections
                now = time.time()
                expired_connections = [conn for conn, t in self.connections.items() if now - t > 900]
                for conn in expired_connections:
                    del self.connections[conn]

                # remove inactive peers
                expired_peers = []
                for peer, files_dict in self.peers.items():
                    expired_files = []
                    for file_hash, peer_info in files_dict.items():
                        if now - peer_info.announce_time > 300:
                            expired_files.append(file_hash)

                    for file_hash in expired_files:
                        if self.peers[peer][file_hash].left > 0:
                            self.files[file_hash]["leechers"].discard(peer)
                        else:
                            self.files[file_hash]["seeders"].discard(peer)

                        del self.peers[peer][file_hash]

                    if not self.peers[peer]:  # remove empty peers
                        expired_peers.append(peer)

                logging.info("Expired peers: " + str(expired_peers))
                for peer in expired_peers:

                    del self.peers[peer]
            
            logging.info("Cleanup complete.")


    def run(self): # runs tracker using multithreading
        thread1 = threading.Thread(target=self.await_message, daemon=True)
        thread2 = threading.Thread(target=self.cleanup, daemon=True)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()


if __name__ == "__main__":
    ip = input("Enter the ip you want to track from (Leave blank for 'localhost'): ").strip()
    port = input("Enter the port you want to listen on (Default: 9999): ")

    tracker = Tracker(ip if ip else "localhost", int(port) if port else 9999)
    tracker.run()
