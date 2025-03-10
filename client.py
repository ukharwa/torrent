import socket
import json
from protocol import *

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "196.42.75.186"
tracker_port = 6969
client_ip = socket.gethostbyname(socket.gethostname)
peerID = generate_peerid(client_ip, "Hello")

protocol = Request()

#decode .cum into variables
#take in a file.cum 
with open(input("Enter torrent file:"),"r") as torrent_file:
    torrent_data = json.load(torrent_file)
    actual_file_size = torrent_data["file_size"]
    file_hash = torrent_data["file_hash"]

downloaded = 0
uploaded = 0
left = actual_file_size
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
    print(seeders)

def seed(response):
    pass

leech(response)
