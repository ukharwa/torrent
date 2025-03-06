import socket
from seeder import Seeder
from protocol import Request

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('192.168.237.254', 6969))

protocol = Request()

files = {
    "file1.txt" : [],
    "file2.txt" : [],
    "file3.txt" : [],
    "file4.txt" : []
}

while True:
    data, addr = tracker.recvfrom(4)
    action = int.from_bytes(data[0:4])

    if action == 0:
        tracker.sendto(protocol.connection_response(), addr)

    # if type == 2:
    #     print("Leecher requesting file")
    #     file = content
    #     seeders = []
        
    #     if file in files:
    #         for s in files[file]:
    #             if s.status == 1:
    #                 seeders.append(s)

    #         if len(seeders) == 0:
    #             protocol.sendMessage("No seeders available", addr[0], addr[1])
    #         else:
    #             seeder = seeders[0]
    #             seeder.status = 2
    #             protocol.sendMessage("Seeder found", addr[0], addr[1])
    #             protocol.sendIP(seeder.ip, seeder.port, addr[0], addr[1])
    #             protocol.sendIP(addr[0], addr[1], seeder.ip, seeder.port)
    #             protocol.sendMessage(file, addr[0], addr[1])

    #     else:
    #         protocol.sendMessage("File not found", addr[0], addr[1])
        
    #     continue

    # if type == 3:
    #     print("Seeder online")
    #     protocol.sendMessage("Seeder online", addr[0], addr[1])
    #     file = content
    #     for s in files[file]:
    #         if s.ip == addr[0]:
    #             s.status = 1
        
    #     continue

    # if type == 4:
    #     print("Seeder offline")
    #     file = content
    #     for s in files[file]:
    #         if s.ip == addr[0]:
    #             s.status = 0

    #     continue
        
    
        
        

