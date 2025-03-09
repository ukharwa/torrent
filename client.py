import socket
from protocol import Request, decode_connectionID

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "localhost"
tracker_port = 6969

protocol = Request()

while True:
    print("Searching for tracker...")
    client.sendto(protocol.connection_request(), (tracker_ip, tracker_port))
    data, _ = client.recvfrom(12)
    action = int.from_bytes(data[0:4], 'little')

    if action == 0:
        print("Tracker found")
        response = protocol.client_decode(data)
        connectionID = response["connectionID"]

        print("Attempting connection...")
        announce = protocol.announce_request(connectionID, "file000000000001.txt", "ukharwa0000000000000", 0, 0, 768000, 1, "192.168.237.129", 9000)
        client.sendto(announce, (tracker_ip, tracker_port))

        data, _ = client.recvfrom(1024)
        response = protocol.client_decode(data)
        action = int.from_bytes(data[0:4], 'little')       
        
        if action == 99:
            print("ERROR: " + response["ERROR"])

        if action == 1:
            print("Successfully connected to tracker...")
        break

print(response)
