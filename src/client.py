
import socket, json, threading, os, base64
from src.peer import generate_peerid
from src.protocol import *

class Client():

    def __init__(self, filename, logger, port=9001, sk="hello"):
        #intialise client with torrent info,logger,port. secret key
        self.torrent_info = self.read_torrent_file(filename)
        self.check_cache()
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = Protocol()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.peerID = generate_peerid(self.ip, sk)
        self.lock = threading.Lock()
        self.logger = logger


    def read_torrent_file(self, filename):
        #read torrent file
        with open(filename,"r") as torrent_file:
            data = json.load(torrent_file)
        return data

     
    def check_cache(self):
        #check if cahce file exists else create default cache
        try:
            with open("cache/." + self.torrent_info["info hash"], "r") as file:
                data = json.load(file)

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
        self.status = 0 if self.cache["left"] == 0 else 1


    def update_cache(self):
        #update cache file with current data
        self.logger.info("Updating cache file")
        self.status = 0 if self.cache["left"] == 0 else 1
        with open("cache/."+self.torrent_info["info hash"], "w") as file:
                json.dump(self.cache, file, indent=4)


    def join_swarm(self, tracker):
        #peer join swarm
        self.logger.info("Joining swarm...")
        attempts = 0
        while attempts < 5:

            announce = self.protocol.announce_request(self.connectionID, self.torrent_info["info hash"], self.peerID, self.cache["downloaded"], self.cache["uploaded"], self.cache["left"], 1, self.ip, self.port)
            self.udp_client.sendto(announce, tracker)

            data, _ = self.udp_client.recvfrom(1024)
            action = int.from_bytes(data[0:4], 'little') 
            response = self.protocol.client_decode(data)

            if action == 1:
                return response
            if action == 99:
                self.logger.error("ERROR: " + response["ERROR"])
                attempts += 1
                self.logger.info(f"Retrying connection (attempt {attempts}/5)...")
                self.connectionID = self.connect_to_tracker(tracker)
                continue  # Try again
            else:
                return None


    def update_tracker(self, tracker, event):   
        #repeatedly sends client's status to the tracker,
        #updates the interval from tracker response, and 
        # reattempts joining swarm if an error occurs

        while True:
            self.logger.info("Updating tracker...")

            announce = self.protocol.announce_request(self.connectionID, self.torrent_info["info hash"], self.peerID, self.cache["downloaded"], self.cache["uploaded"], self.cache["left"], event, self.ip, self.port)
            self.udp_client.sendto(announce, tracker)

            data, _ = self.udp_client.recvfrom(1024)
            action = int.from_bytes(data[0:4], 'little') 
            response = self.protocol.client_decode(data)

            if action == 1:
                self.update_interval = response["interval"]
                return response
            if action == 99:
                self.join_swarm(tracker)
            time.sleep(self.update_interval)


    def connect_to_tracker(self, tracker):
        #connect to tracker and get connection id
        self.logger.info("Searching for tracker...")
        self.udp_client.sendto(self.protocol.connection_request(), tracker)
        data, _ = self.udp_client.recvfrom(12)
        action = int.from_bytes(data[0:4], 'little')
        response = self.protocol.client_decode(data)

        if action == 0:
            self.logger.info("Tracker found")
            return response["connectionID"]


    def request_piece(self, seeder, piece_list):
            #request for pieces from seeder using tcp
            try:
                counter = 0
                index = 0
                tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_client.connect(seeder)
                while len(piece_list) > 0:
                    if counter == 3:
                        counter = 0
                        index += 1  
                    piece_index = piece_list[index]
                    self.logger.info(f"Connected to {seeder} for piece {piece_index}")

                    tcp_client.send(piece_index.to_bytes(4, 'little'))

                    piece_size = int.from_bytes(recv_all(tcp_client, 4), "little")
                    received_index = int.from_bytes(recv_all(tcp_client, 4), "little")

                    piece = recv_all(tcp_client, piece_size)

                    if base64.b64encode(hashlib.sha256(piece).digest()).decode("utf-8") == self.torrent_info["pieces"][piece_index]:
                        self.logger.info(f"Piece {piece_index} received")
                        offset = piece_index * self.torrent_info["piece length"]

                        with self.lock:
                            with open(self.cache["file path"], "r+b") as f:
                                f.seek(offset)
                                f.write(piece) 

                            self.cache["left"] -= len(piece)
                            self.cache["downloaded"] += len(piece)
                            self.cache["pieces"][received_index] = 1
                            piece_list.pop(0)

                    else:
                        self.logger.info(f"Incorrect hash for piece {piece_index}")
                        counter += 1

                tcp_client.send(b"\xff")

                tcp_client.close()

            except ConnectionRefusedError:
                self.logger.info(f"Failed to connect to {seeder}")


    def leech(self, response):
        #download pieces from seeders
        try:
            seeders = response["seeders"]

            if not seeders:
                self.logger.info("No seeders available")
                return

            if not os.path.exists(self.cache["file path"]):
                with open(self.cache["file path"], "wb") as f:
                    f.truncate(self.torrent_info["file size"])

            threads = []
            
            missing_pieces = [i for i, has_piece in enumerate(self.cache["pieces"]) if has_piece == 0]

            # Distribute pieces among seeders (round-robin)
            seeder_pieces = {seeder: [] for seeder in seeders}
            seeder_count = len(seeders)
            for i, piece_index in enumerate(missing_pieces):
                seeder = seeders[i % seeder_count]  # Manually cycle through seeders
                seeder_pieces[seeder].append(piece_index)

            # start one thread per seeder
            threads = []
            for seeder, piece_list in seeder_pieces.items():
                thread = threading.Thread(target=self.request_piece, args=(seeder, piece_list))
                thread.start()
                threads.append(thread)

            #wait for all threads to finish
            for thread in threads:
                thread.join()

            #save the downloaded file
            self.logger.info("Download complete!")

        finally:
            self.update_cache()
            self.update_tracker(self.tracker, 3)


    def seed(self):
        #server pieces to requesting peers
        try:
            tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server.bind((socket.gethostbyname(socket.gethostname()), self.port))
            tcp_server.listen()

            self.logger.info("Seeding " + self.torrent_info["file name"] + "...")
            while True:
                try:
                    self.logger.info("Seeding: waiting for peer connection...")
                    conn, addr = tcp_server.accept()
                    self.logger.info(f"Peer connected from {addr}")

                    while True:
                        piece_data = recv_all(conn, 4)
                        # Check if seeder should stop
                        if piece_data.hex() == "ff":
                            self.logger.info("Seeder received termination signal.")
                            break
                        piece_index = int.from_bytes(piece_data, 'little')
                        self.logger.info(f"Request for piece {piece_index}")
                        # Corrected: subtract 4 from the length of the packet data (header excluded)
                        piece = get_packets(self.cache["file path"], piece_index, self.torrent_info["piece length"])
                        conn.sendall(piece)
                        self.logger.info("Piece sent")
                        self.cache["uploaded"] += int.from_bytes(piece[0:4], "little") - 4

                    conn.close()
                except:
                    self.logger.warning("Leecher unexpectedly disconnected")
                finally:
                    self.update_cache()
                    self.logger.info("Seeding ended and cache updated.")
        finally:
            self.logger.error("An error occured. Leaving swarm...")
            self.update_cache()
            self.update_tracker(self.tracker, 3)


    def run(self):

        self.tracker = tuple(self.torrent_info["tracker"])
        self.connectionID = self.connect_to_tracker(self.tracker)

        response = self.join_swarm(self.tracker)

        threads = []

        if response:
            self.update_interval = response["interval"]

            update_thread = threading.Thread(target=lambda: self.update_tracker(self.tracker, 0))
            save_thread = threading.Thread(target=self.save_cache)
            threads.append(update_thread)
            threads.append(save_thread)

            if self.status == 0:
                seed_thread = threading.Thread(target=self.seed)
                threads.append(seed_thread)
            else:
                leech_thread = threading.Thread(target= lambda: self.leech(response))
                threads.append(leech_thread)
        else:
            self.logger.info("Could not establish connection to tracker")
            return

        for thread in threads:
            thread.start()


    def save_cache(self):
        #periodically cache file progress
        time.sleep(5)
        self.update_cache()

    def get_name(self):
        return self.torrent_info["file name"]
    
    def get_status(self):
        return self.status

    def get_percentage(self):
        return self.cache["downloaded"] / self.torrent_info["file size"]
