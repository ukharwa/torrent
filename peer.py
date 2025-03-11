import hashlib

class Peer:
    def __init__(self, ip, port, downloaded, uploaded, left, event, announce_time):
        self.ip = ip
        self.port = port
        self.downloaded = downloaded
        self.uploaded = uploaded
        self.left = left
        self.announce_time = announce_time
        self.event = event

    
def generate_peerid(ip, secretkey):
    return hashlib.sha256((ip+secretkey).encode()).hexdigest()

