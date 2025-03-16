import json

def create_cache(torrent, path):
        with open(torrent,"r") as torrent_file:
                torrent_info = json.load(torrent_file)

        data = {
                "file path": path,
                "downloaded": torrent_info["file size"],
                "uploaded": 0,
                "left": 0,
                "pieces": len(torrent_info["pieces"])
                }

        with open("cache/."+torrent_info["info hash"], "w") as file:
                json.dump(data, file, indent=4)  # Write JSON data with pretty formatting
