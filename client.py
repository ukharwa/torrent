import socket
import json
from protocol import *

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "196.42.75.186"
tracker_port = 6969
client_ip = socket.gethostbyname(socket.gethostname())
client_port = 9001
peerID = generate_peerid(client_ip, "Hello")

protocol = Request()

#decode .ppp into variables
#take in a file.ppp 
with open(input("Enter torrent file:"),"r") as torrent_file:
    torrent_data = json.load(torrent_file)
    actual_file_size = torrent_data["file_size"]
    file_hash = torrent_data["file_hash"]
    packet_list = torrent_data["packet_list"]

downloaded = 0
uploaded = 0
left = 0
error_count = 0

while True:
    if error_count == 5:
        print("ERROR: Too many errors, exiting...")
        break
    print("Searching for tracker...")
    udp_client.sendto(protocol.connection_request(), (tracker_ip, tracker_port))
    data, _ = udp_client.recvfrom(12)
    action = int.from_bytes(data[0:4], 'little')

    if action == 0:
        print("Tracker found")
        response = protocol.client_decode(data)
        connectionID = response["connectionID"]

        print("Attempting connection...")
        announce = protocol.announce_request(connectionID, file_hash, peerID, 0, 0, left, 1, client_ip, 9000)
        udp_client.sendto(announce, (tracker_ip, tracker_port))

        data, _ = udp_client.recvfrom(1024)
        response = protocol.client_decode(data)
        action = int.from_bytes(data[0:4], 'little')       
        
        if action == 99:
            print("ERROR: " + response["ERROR"])
            error_count += 1
        if action == 1:
            print("Successfully connected to tracker...")
            print(response)
            break

tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def leech(response):
    seeders = response["seeders"]
    #list of seeders :(ip,port)
    for s in seeders:
        tcp_client.connect(s)

    file = []

    while len(packet_list > 0):
        tcp_client.send(packet_list[0].encode())
        packet = tcp_client.recv(512*1024)
        if hashlib.sha256(packet) == packet_list[0]:
            file.append(packet)
            packet_list.pop(packet_list[0])
    
    tcp_client.send(0)

    with open("new_file.png", "wb") as new_file:
        for p in file:
            new_file.write(p)
    new_file.close()

def seed(filename):
    tcp_client.bind((client_ip,client_port))
    tcp_client.listen()

    packets = getpackets(filename, 512*1024)

    conn, addr = tcp_client.accept()

    while True:
        packet_hash = conn.recv(32).decode()
        if packet_hash == 0:
            break
        conn.send(packets[packet_hash])
    
    tcp_client.close()