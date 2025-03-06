import socket
from protocol import Request

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "192.168.237.254"
tracker_port = 6969

protocol = Request()

while True:
    client.sendto(protocol.connection_request(), (tracker_ip, tracker_port))
    response, _ = client.recvfrom(4)
    action = int.from_bytes(response[0:4], 'little')
    if action == 0:
        print("Connected to Tracker")
        break
