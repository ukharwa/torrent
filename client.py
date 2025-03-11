import socket, json
from src.peer import *
from src.protocol import *
from testgui import gui

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
protocol = Request()

def read_torrent_file(filename):
    with open(filename,"r") as torrent_file:
        data = json.load(torrent_file)
    return data

 
def check_cache(torrent_info):
    try:
        with open("cache/."+torrent_info["info hash"], "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        data = {
            "file path": "downloads/"+torrent_info["file name"],
            "downloaded": 0,
            "uploaded": 0,
            "left": torrent_info["file size"],
            "pieces": len(torrent_info["pieces"])
        }

        with open("cache/."+torrent_info["info hash"], "w") as file:
            json.dump(data, file, indent=4)  # Write JSON data with pretty formatting
        
        return data


def update_cache(cache_name, data):
    with open("cache/."+cache_name, "w") as file:
            json.dump(data, file, indent=4)


def connect_to_tracker(tracker, file_hash, downloaded, uploaded, left, ip, port):
    while True:
        print("Searching for tracker...")
        udp_client.sendto(protocol.connection_request(), tracker)
        data, _ = udp_client.recvfrom(12)
        action = int.from_bytes(data[0:4], 'little')

        if action == 0:
            print("Tracker found")
            response = protocol.client_decode(data)
            connectionID = response["connectionID"]

            print("Attempting connection...")
            announce = protocol.announce_request(connectionID, file_hash, generate_peerid(ip, "Hello"), downloaded, uploaded, left, 1, ip, port)
            udp_client.sendto(announce, tracker)

            data, _ = udp_client.recvfrom(1024)
            response = protocol.client_decode(data)
            action = int.from_bytes(data[0:4], 'little')       
            
            if action == 99:
                print("ERROR: " + response["ERROR"])

            if action == 1:
                print("Successfully connected to tracker...")
                print(response)
                break
    return response


def leech(torrent_info, cache, response):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    seeders = response["seeders"]

    for s in seeders:
        tcp_client.connect(s)

    pieces = torrent_info["pieces"]

    file = []

    for p in pieces:
        tcp_client.send(bytes.fromhex(p))
        
        piece_size = tcp_client.recv(4)
        piece = recv_all(tcp_client, int.from_bytes(piece_size, "little"))

        if hashlib.sha256(piece).hexdigest() == p:
            print("packet received")
            file.append(piece)
            cache["left"] -= len(piece)
            cache["downloaded"] += len(piece)
            
    
    tcp_client.send(b"\xff")

    with open(cache["file path"], "wb") as new_file:
        for p in file:
            new_file.write(p)

    update_cache(torrent_info["file hash"], cache)
    

def seed(torrent_info, cache, port):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.bind((socket.gethostbyname(socket.gethostname()),port))
    tcp_client.listen()

    packets = getpackets(cache["file path"], torrent_info["piece length"])

    conn, _ = tcp_client.accept()

    while True:
        piece_hash = conn.recv(32).hex()
        if piece_hash == "ff":
            print("breaking")
            break
        conn.sendall(packets[piece_hash])
        cache["uploaded"] += len(packets[piece_hash] - 4)
    
    tcp_client.close()

    update_cache(torrent_info["file hash"], cache)


def main():

    torrent_file = gui()
    torrent_info = read_torrent_file(torrent_file)
    
    cache = check_cache(torrent_info)

    client_port = 9001
    
    downloaded = cache["downloaded"]
    uploaded = cache["uploaded"]
    left = cache["left"]

    print(tuple(torrent_info["tracker"]))
    response = connect_to_tracker(tuple(torrent_info["tracker"]), torrent_info["info hash"], downloaded, uploaded, left, socket.gethostbyname(socket.gethostname()), client_port)

    if cache["left"] == 0:
        print("Seeding...")
        seed(torrent_info, cache, 9001)
    else:
        print("Leeching")
        leech(torrent_info, cache, response)

main()