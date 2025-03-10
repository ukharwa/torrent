import hashlib
import json
#minimum packet size is 512kb
packet_size = 512 * 1024  # 512KB

def getnumpackets(filename):
    with open(filename, "rb") as file:
        data = file.read()
        total_size = len(data)                  # Total size of the file in bytes
        num_packets = total_size // packet_size # Number of packets required to send the data
        if total_size % packet_size != 0:       # If file size is not perfectly divisible by num_packets, adjust the last packet    
            num_packets += 1   
    file.close()
    return num_packets if num_packets != 0 else 1 

def getpackets(filename):
    with open(filename, "rb") as file:
        data = file.read()
        num_packets = getnumpackets(filename)
    file.close()
    packets = []
    
    # If file size is not perfectly divisible by num_packets, adjust the last packet
    for i in range(num_packets):
        packet = data[i * packet_size: (i + 1) * packet_size]  # Slice the data into packets
        packets.append(packet)  # Append each packet to the list
    return packets


def filetotorrent(filename):            #reads a file and populates another file with the torrent data
    with open(filename, "rb") as file:            
        data = file.read()
        total_size = len(data)                  # Total size of the file in bytes
    num_packets = getnumpackets(filename)       # Number of packets required to send the data
    packets = getpackets(filename)             # List of packets

    # for i,val in enumerate(packets):
    #     print(f"{i} {len(val)}")
    
    size_of_packets = [len(packet) for packet in packets] #size of each packet in bytes
    file_hash = hashlib.sha256(data).hexdigest() #hash of the original file in bytes
    file_packet_hashes = [hashlib.sha256(packet).hexdigest() for packet in packets] #hosh of each packet in bytes

    torrent_data = {
        "file_hash": file_hash,
        "file_size": total_size,
        "num_packets": num_packets,
        "size_of_packets": size_of_packets,
        "packet_list": file_packet_hashes
    }

    torrent_filename = file.name.split(".")[0] + ".ppp"

    with open(torrent_filename, "w") as torrent_file:
        json.dump(torrent_data, torrent_file, indent=4)  # Write JSON data with pretty formatting
        


filename = input("Enter file name: ")
filetotorrent(filename)
    
