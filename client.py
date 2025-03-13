
import socket, json, threading
from src.peer import generate_peerid
from src.protocol import *


class Client():
    def __init__(self, port=9001, sk="hello"):
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = Protocol()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.peerID = generate_peerid(self.ip, sk)

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
                "pieces": len(self.torrent_info["pieces"])
            }

            with open("cache/."+self.torrent_info["info hash"], "w") as file:
                json.dump(data, file, indent=4)  # Write JSON data with pretty formatting
            
            self.cache = data


    def update_cache(self):
        with open("cache/."+self.torrent_info["info hash"], "w") as file:
                json.dump(self.cache, file, indent=4)


    def update_tracker(self, tracker, event):
        attempts = 0
        while attempts < 5:
            print("Joining swarm...")

            announce = self.protocol.announce_request(self.connectionID, self.torrent_info["info hash"], self.peerID, self.cache["downloaded"], self.cache["uploaded"], self.cache["left"], event, self.ip, self.port)
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

    def connect_to_tracker(self, tracker):
        print("Searching for tracker...")
        self.udp_client.sendto(self.protocol.connection_request(), tracker)
        data, _ = self.udp_client.recvfrom(12)
        action = int.from_bytes(data[0:4], 'little')
        response = self.protocol.client_decode(data)

        if action == 0:
            print("Tracker found")
            return response["connectionID"]
           

    def leech(self, response):
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        seeders = response["seeders"]
        print(seeders[0])
        
        count = 1
        while count <= 20:
            print(f"Trying to connect to seeder... ({count})")
            try:
                tcp_client.connect(seeders[0])
                break
            except ConnectionRefusedError:
                count += 1
                continue

        pieces = self.torrent_info["pieces"]

        file = []

        for p in pieces:
            tcp_client.send(bytes.fromhex(p))
            
            piece_size = tcp_client.recv(4)
            piece = recv_all(tcp_client, int.from_bytes(piece_size, "little"))

            if hashlib.sha256(piece).hexdigest() == p:
                print("packet received")
                file.append(piece)
                self.cache["left"] -= len(piece)
                self.cache["downloaded"] += len(piece)
                
        
        tcp_client.send(b"\xff")

        with open(self.cache["file path"], "wb") as new_file:
            for p in file:
                new_file.write(p)

        self.update_cache()
        

    def seed(self):
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind((socket.gethostbyname(socket.gethostname()), self.port))
        tcp_server.listen()

        packets = getpackets(self.cache["file path"], self.torrent_info["piece length"])

        print("Seeding: waiting for peer connection...")
        conn, addr = tcp_server.accept()
        print(f"Peer connected from {addr}")

        while True:
            piece_hash_data = conn.recv(32)
            # Check if seeder should stop
            if piece_hash_data.hex() == "ff":
                print("Seeder received termination signal.")
                break

            piece_hash = piece_hash_data.hex()
            if piece_hash in packets:
                # Corrected: subtract 4 from the length of the packet data (header excluded)
                conn.sendall(packets[piece_hash])
                self.cache["uploaded"] += len(packets[piece_hash]) - 4
            else:
                print(f"Requested piece {piece_hash} not found.")
        conn.close()
        tcp_server.close()

        self.update_cache()
        print("Seeding complete and cache updated.")


    def run(self, filename):
        self.torrent_info = self.read_torrent_file(filename)
        
        self.check_cache()
        
        tracker = tuple(self.torrent_info["tracker"])

        self.connectionID = self.connect_to_tracker(tracker)
        response = self.update_tracker(tracker, 1)

        if response:
            self.update_interval = response["interval"]
            if self.cache["left"] == 0:
                print("Seeding...")
                self.seed()
            else:
                print("Leeching")
                self.leech(response)
        else:
            print("Could not establish connection to tracker")

client = Client()
client.run("image69.ppp")

