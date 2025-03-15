import hashlib
import json
import base64

def generate_packet_hashes(filename, packet_size):

    packets = []

    with open(filename, "rb") as file:
        while packet := file.read(packet_size):
            packets.append(base64.b64encode(hashlib.sha256(packet).digest()).decode("utf-8"))
    file.close()
    
    return packets

def generate_torrent_data(filename, piece_size, tracker_ip, tracker_port):

    with open(filename, "rb") as file:            
        data = file.read()
    
    file_size = len(data)           # Total size of the file in bytes
    if file_size < piece_size:
        piece_size = file_size       
    info_hash = hashlib.sha256(data).hexdigest() #hash of the original file in bytes
    packets = generate_packet_hashes(filename, piece_size)             # List of packets

    torrent_data =  {
        "tracker": (tracker_ip, tracker_port),
        "file name": filename.split("\\")[-1],
        "info hash": info_hash,
        "file size": file_size,
        "piece length": piece_size,
        "pieces": packets 
    }

    return torrent_data


def filetotorrent(filename, piece_size, tracker_ip, tracker_port):            #reads a file and populates another file with the torrent data

    torrent_data = generate_torrent_data(filename, piece_size, tracker_ip, tracker_port)
    torrent_filename = filename.split("/")[-1].split(".")[0] + ".ppp"

    with open(torrent_filename, "w") as torrent_file:
        json.dump(torrent_data, torrent_file, indent=4)  # Write JSON data with pretty formatting
        
    
