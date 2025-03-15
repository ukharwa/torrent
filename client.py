
import socket, json, threading, os
from src.peer import generate_peerid
from src.protocol import *


class Client():
    def __init__(self, port=9001, sk="hello"):
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = Protocol()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.peerID = generate_peerid(self.ip, sk)
        self.lock = threading.Lock()

    def read_torrent_file(self, filename):
        with open(filename,"r") as torrent_file:
            data = json.load(torrent_file)
        return data

     
    def check_cache(self):
        try:
            with open("cache/." + self.torrent_info["info hash"], "r") as file:
                data = json.load(file)
            self.cache = data 
        except FileNotFoundError:
            data = {
                "file path": "downloads/"+ self.torrent_info["file name"],
                "downloaded": 0,
                "uploaded": 0,
                "left": self.torrent_info["file size"],
                "pieces": [0] * len(self.torrent_info["pieces"])
            }

            with open("cache/."+self.torrent_info["info hash"], "w") as file:
                json.dump(data, file, indent=4)  # Write JSON data with pretty formatting
            
            self.cache = data


    def update_cache(self):
        with open("cache/."+self.torrent_info["info hash"], "w") as file:
                json.dump(self.cache, file, indent=4)


    def join_swarm(self, tracker):
        attempts = 0
        while attempts < 5:
            print("Joining swarm...")

            announce = self.protocol.announce_request(self.connectionID, self.torrent_info["info hash"], self.peerID, self.cache["downloaded"], self.cache["uploaded"], self.cache["left"], 1, self.ip, self.port)
            self.udp_client.sendto(announce, tracker)

            data, _ = self.udp_client.recvfrom(1024)
            action = int.from_bytes(data[0:4], 'little') 
            response = self.protocol.client_decode(data)

            if action == 1:
                return response
            if action == 99:
                print("ERROR: " + response["ERROR"])
                attempts += 1
                print(f"Retrying connection (attempt {attempts}/5)...")
                self.connectionID = self.connect_to_tracker(tracker)
                continue  # Try again
            else:
                return None

    def update_tracker(self, tracker):
        while True:
            time.sleep(self.update_interval)
            print("Updating tracker...")

            announce = self.protocol.announce_request(self.connectionID, self.torrent_info["info hash"], self.peerID, self.cache["downloaded"], self.cache["uploaded"], self.cache["left"], 0, self.ip, self.port)
            self.udp_client.sendto(announce, tracker)

            data, _ = self.udp_client.recvfrom(1024)
            action = int.from_bytes(data[0:4], 'little') 
            response = self.protocol.client_decode(data)

            if action == 1:
                self.update_interval = response["interval"]
                return response
            if action == 99:
                return None

    def connect_to_tracker(self, tracker):
        print("Searching for tracker...")
        self.udp_client.sendto(self.protocol.connection_request(), tracker)
        data, _ = self.udp_client.recvfrom(12)
        action = int.from_bytes(data[0:4], 'little')
        response = self.protocol.client_decode(data)

        if action == 0:
            print("Tracker found")
            return response["connectionID"]


    def request_piece(self, seeder, piece_index):
            try:
                tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_client.connect(seeder)
                print(f"Connected to {seeder} for piece {piece_index}")

                tcp_client.send(piece_index.to_bytes(1, 'little'))

                piece_size = int.from_bytes(recv_all(tcp_client, 4), "little")
                received_index = int.from_bytes(recv_all(tcp_client, 4), "little")

                piece = recv_all(tcp_client, piece_size)

                if hashlib.sha256(piece).hexdigest() == self.torrent_info["pieces"][piece_index]:
                    print(f"Piece {piece_index} received")
                    offset = piece_index * self.torrent_info["piece length"]

                    with self.lock:
                        with open(self.cache["file path"], "r+b") as f:
                            f.seek(offset)
                            f.write(piece) 

                        self.cache["left"] -= len(piece)
                        self.cache["downloaded"] += len(piece)
                        self.cache["pieces"][received_index] = 1

                else:
                    print(f"Incorrect hash for piece {piece_index}")

                tcp_client.send(b"\xff")

                tcp_client.close()

            except ConnectionRefusedError:
                print(f"Failed to connect to {seeder}")

    def leech(self, response):

        seeders = response["seeders"]

        if not seeders:
            print("No seeders available")
            return

        if not os.path.exists(self.cache["file path"]):
            with open(self.cache["file path"], "wb") as f:
                f.truncate(self.torrent_info["file size"])

        threads = []
        piece_indices = [i for i, have_piece in enumerate(self.cache["pieces"]) if have_piece == 0]

        # Distribute piece requests among available seeders
        for i, piece_index in enumerate(piece_indices):
            seeder = seeders[i % len(seeders)]  # Round-robin seeders
            thread = threading.Thread(target=lambda: self.request_piece(seeder, piece_index))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Save the downloaded file
        self.update_cache()
        print("Download complete!")


    def seed(self):
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind((socket.gethostbyname(socket.gethostname()), self.port))
        tcp_server.listen()

        pieces = getpackets(self.cache["file path"], self.torrent_info["piece length"])
        print("Seeding " + self.torrent_info["file name"] + "...")
        while True:
            print("Seeding: waiting for peer connection...")
            conn, addr = tcp_server.accept()
            print(f"Peer connected from {addr}")

            while True:
                piece_data = conn.recv(32)
                # Check if seeder should stop
                if piece_data.hex() == "ff":
                    print("Seeder received termination signal.")
                    break
                piece_index = int.from_bytes(piece_data, 'little')
                print(f"Request for piece {piece_index}")
                if piece_index in range(0, len(pieces)):
                    # Corrected: subtract 4 from the length of the packet data (header excluded)
                    conn.sendall(pieces[piece_index])
                    print("Piece sent")
                    self.cache["uploaded"] += len(pieces[piece_index]) - 4
                else:
                    print(f"Requested piece {piece_index} not found.")
            conn.close()

            self.update_cache()
            print("Seeding complete and cache updated.")


    def run(self, filename):
        self.torrent_info = self.read_torrent_file(filename)
        
        self.check_cache()
        
        tracker = tuple(self.torrent_info["tracker"])

        self.connectionID = self.connect_to_tracker(tracker)
        response = self.join_swarm(tracker)

        threads = []
        if response:
            self.update_interval = response["interval"]
            update_thread = threading.Thread(target=lambda: self.update_tracker(tracker))
            threads.append(update_thread)
            if self.cache["left"] == 0:
                seed_thread = threading.Thread(target=self.seed)
                threads.append(seed_thread)
            else:
                leech_thread = threading.Thread(target= lambda: self.leech(response))
                threads.append(leech_thread)
        else:
            print("Could not establish connection to tracker")
            return
        
        for thread in threads:
            thread.start()


client = Client()
client.run(input("Enter .ppp file: "))

