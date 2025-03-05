import socket
from seeder import Seeder
from protocols import TrackerToClient

tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker.bind(('192.168.237.90 ', 6969))
seeder_addr= 0
leecher_addr= 0
port = "6969"

files = {
    "file1.txt" : [Seeder("192.168.237.121", 9999, 0)],
    "file2.txt" : [Seeder("192.168.237.121", 9999, 0)],
    "file3.txt" : [Seeder("192.168.237.121", 9999, 0)],
    "file4.txt" : [Seeder("192.168.237.121", 9999, 0)],
}

while True:
    seeders = []
    data,addr = tracker.recvfrom(260) #SEEDING, 12.345.232.24
    if data[0] == 0:
        print("Seeder connected")
        
    elif data[0] == 1:
        print("Leecher requesting file")
        file = data[6:int.from_bytes(data[2:6],'little')].decode()

        if file not in files:
            message = "File not found"
            data = TrackerToClient(0, len(message).to_bytes(4, 'little'), message.encode())
            continue

        for s in files[file]:
            if s.status == 1:
                seeders.append(s)
        if len(seeders) == 0:
            header[0] = 0
            message = "No seeders availabe; Try again later"
            header[2:6] = len(message).to_bytes(4, 'little')
            header[6:] = message.encode()
            continue
        
        header[0] = 1
        header[1] = 
       
    if seeder_addr != 0 and leecher_addr != 0:
        break

