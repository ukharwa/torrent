import socket, json
from peer import *
from protocol import *

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "localhost"
tracker_port = 6969

protocol = Request()

def read_torrent_file(filename):
    with open(filename,"r") as torrent_file:
        data = json.load(torrent_file)
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


def leech(filename):
    client_ip = socket.gethostbyname(socket.gethostname())
    client_port = 9001

    torrent = read_torrent_file(filename)
    pieces = torrent["pieces"]

    downloaded = 0
    uploaded = 0
    left = 1000

    response = connect_to_tracker(torrent["info hash"], downloaded, uploaded, left, client_ip, client_port)

    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    seeders = response["seeders"]

    for s in seeders:
        tcp_client.connect(s)

    file = []

    while len(pieces) > 0:
        tcp_client.send(pieces[0].encode())
        packet = tcp_client.recv(512*1024)
        if hashlib.sha256(packet) == pieces[0]:
            file.append(packet)
            pieces.pop(pieces[0])
    
    tcp_client.send(b"0")

    with open("new_file.png", "wb") as new_file:
        for p in file:
            new_file.write(p)
    new_file.close()


def seed(torrent_file, filename):
    client_ip = socket.gethostbyname(socket.gethostname())
    client_port = 9001

    torrent = read_torrent_file(torrent_file)
    pieces = torrent["pieces"]

    downloaded = 0
    uploaded = 0
    left = 0

    response = connect_to_tracker(torrent["info hash"], downloaded, uploaded, left, client_ip, client_port)

    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.bind((client_ip,client_port))
    tcp_client.listen()

    packets = getpackets(filename, 512*1024)

    conn, _ = tcp_client.accept()

    while True:
        packet_hash = conn.recv(32).decode()
        if packet_hash == 0:
            break
        conn.send(packets[packet_hash])
    
    tcp_client.close()


torrent_file = input("Enter the .ppp file name: ")
file = input("Enter the file name: ")

leech(torrent_file)
seed(torrent_file, file)

