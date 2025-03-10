import hashlib
import json

def generate_packet_hashes(filename, packet_size):

    packets = []

    with open(filename, "rb") as file:
        while packet := file.read(packet_size):
            packets.append(hashlib.sha256(packet).hexdigest())
    file.close()
    
    return packets
    
def filetotorrent(filename, piece_size, tracker_ip, tracker_port):            #reads a file and populates another file with the torrent data

    with open(filename, "rb") as file:            
        data = file.read()
    file.close()

    file_size = len(data)                  # Total size of the file in bytes
    info_hash = hashlib.sha256(data).hexdigest() #hash of the original file in bytes
    packets = generate_packet_hashes(filename, piece_size)             # List of packets

    file_packet_hashes = [hashlib.sha256(packet).hexdigest() for packet in packets] #hosh of each packet in bytes

    torrent_data = {
        "tracker": (tracker_ip, tracker_port),
        "info hash": info_hash,
        "file size": file_size,
        "piece length": piece_size,
        "pieces": file_packet_hashes
    }

    torrent_filename = file.name.split(".")[0] + ".ppp"

    with open(torrent_filename, "w") as torrent_file:
        json.dump(torrent_data, torrent_file, indent=4)  # Write JSON data with pretty formatting
        


filename = input("Enter file name: ")
piece_size = input("Enter piece size: ")
tracker_ip = input("Enter tracker ip: ")
tracker_port = input("Enter tracker port: ")

filetotorrent(filename, piece_size, tracker_ip, tracker_port)
    
