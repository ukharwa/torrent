import socket
from protocol import Protocol

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tracker_ip = "192.168.237.254"
tracker_port = 6969

protocol = Protocol(client)

while True:
    role = input("L/S: ")

    if role.lower() == "l":
        file = input("Enter the file you want: ")
        protocol.leech(file, tracker_ip, tracker_port)
        break
    elif role.lower() == "s":
        file = input("Enter the file you want to seed: ")
        protocol.seed(file, tracker_ip, tracker_port)
        break
    
    print("Role not available") 


print("Waiting for response...")
data, _ = client.recvfrom(260)
type, message = protocol.receive(data)