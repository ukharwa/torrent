import socket

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = "192.168.237.90"
port = 6969

header = bytearray(261)
# Information sent to tracker
# header[0] = message_type: Leecher (1) or Seeder (0)
# header[2:6] = content length
# rest of header is file name

while True:
    role = input("L/S: ")

    if role.lower() == "l":
        file = input("Enter the file you want: ")
        header[0] = 1
        header[1] = 1
        header[2:6] = len(file).to_bytes(4, 'little')
        header[6:] = file.encode()
        break
    elif role.lower() == "s":
        file = input("Enter the file you want to seed: ")
        header[0] = 1
        header[1] = 1
        header[2:6] = len(file).to_bytes(4, 'little')
        header[6:] = file.encode()
        break
    
    print("Role not available")