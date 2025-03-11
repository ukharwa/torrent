import socket, json
from src.peer import *
from src.protocol import *


udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "localhost"
tracker_port = 6969

protocol = Request()

def read_torrent_file(filename):
    with open(filename,"r") as torrent_file:
        data = json.load(torrent_file)
    return data

def check_cache(torrent_info):
    try:
        with open("."+torrent_info["info hash"], "r") as file:
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

        with open("."+torrent_info["info hash"], "w") as file:
            json.dump(data, file, indent=4)  # Write JSON data with pretty formatting
        
        return data


def connect_to_tracker(file_hash, downloaded, uploaded, left, ip, port):
    while True:
        print("Searching for tracker...")
        udp_client.sendto(protocol.connection_request(), (tracker_ip, tracker_port))
        data, _ = udp_client.recvfrom(12)
        action = int.from_bytes(data[0:4], 'little')

        if action == 0:
            print("Tracker found")
            response = protocol.client_decode(data)
            connectionID = response["connectionID"]

            print("Attempting connection...")
            announce = protocol.announce_request(connectionID, file_hash, generate_peerid(ip, "Hello"), downloaded, uploaded, left, 1, ip, port)
            udp_client.sendto(announce, (tracker_ip, tracker_port))

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


def leech(torrent_info, cache):
    client_ip = socket.gethostbyname(socket.gethostname())
    client_port = 9001

    pieces = torrent_info["pieces"]

    downloaded = cache["downloaded"]
    uploaded = cache["uploaded"]
    left = cache["left"]

    response = connect_to_tracker(torrent_info["info hash"], downloaded, uploaded, left, client_ip, client_port)

    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    seeders = response["seeders"]

    for s in seeders:
        tcp_client.connect(s)

    file = []

    for p in pieces:
        tcp_client.send(bytes.fromhex(p))
        
        piece_size = tcp_client.recv(4)
        piece = recv_all(tcp_client, int.from_bytes(piece_size, "little"))

        print(len(piece))
        if hashlib.sha256(piece).hexdigest() == p:
            print("packet received")
            file.append(piece)
    
    tcp_client.send(b"\xff")

    with open("test_file.png", "wb") as new_file:
        for p in file:
            new_file.write(p)


def seed(torrent_info, cache):
    client_ip = socket.gethostbyname(socket.gethostname())
    client_port = 9001

    pieces = torrent_info["pieces"]

    downloaded = cache["downloaded"]
    uploaded = cache["uploaded"]
    left = cache["left"]

    response = connect_to_tracker(torrent_info["info hash"], downloaded, uploaded, left, client_ip, client_port)

    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.bind((client_ip,client_port))
    tcp_client.listen()

    packets = getpackets(cache["file path"], torrent_info["piece length"])

    conn, _ = tcp_client.accept()

    while True:
        piece_hash = conn.recv(32).hex()
        if piece_hash == "ff":
            print("breaking")
            break
        conn.sendall(packets[piece_hash])
    
    tcp_client.close()


def main():
    torrent_file = input("Enter name of torrent (.ppp) file: ")
    torrent_info = read_torrent_file(torrent_file)

    cache_info = check_cache(torrent_info["file name"], torrent_info["info hash"], len(torrent_info["pieces"]))

    if cache_info["left"] == 0:
        seed(torrent_info, cache_info)
    else:
        leech(torrent_file, cache_info)

main()