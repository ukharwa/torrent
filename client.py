import socket
from protocol import Request

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "196.42.75.61"
tracker_port = 6969

protocol = Request()

while True:
    client.sendto(protocol.connection_request(), (tracker_ip, tracker_port))
    response, _ = client.recvfrom(4)
    action = int.from_bytes(response[0:4], 'little')
    if action == 0:
        print("Connected to Tracker")
        break

announce = protocol.announce_request("file1.txt", "ukharwa", 0, 0, 768000, 1, "196.42.75.61", 9000)
client.sendto(announce, (tracker_ip, tracker_port))
data, _ = client.recvfrom(20)
interval, leechers, seeders = protocol.decode(data)
print("interval: " + str(interval))
print("leechers: " + str(leechers))
print("seeders: " + str(seeders))