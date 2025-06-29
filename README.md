# Peer-to-Peer Protocol

A simple peer-to-peer file sharing system.
Implements a simple UDP tracker to facilitate connections.
Allows for concurrent seeding and leeching and leeching from multiple seeders for the same file.
Implements SHA-256 integrity checks.

---
## Instructions
1. Download all the files
2. Run the tracker (see TRACKER section below)
3. Seed the file (see SEEDING section below)
4. Leech the file (see LEECHING section below)

### TRACKER:
	1. Run the file 'tracker.py'. This will ask you for an ip and a port to listen on. Defaults = ("localhost", 9999)

### SEEDING:
	1. Run the file main.py. This will open up a gui with a select file button.
	2. Select a file you want to seed. This will generate a .ppp torrent file for the file you are seeding and begin seeding.
	3. If you already have a .ppp file and you have completed the download you can select the .ppp file and seed from there

### LEECHING:
	1. Run main.py
	2. Click the "Select file" button
	3. Choose a .ppp file
	4. If a seeder is seeding that file your download will begin, otherwise try again later.
	5. The file will save in the downloads folder.
---
## NOTES:
When you are seeding a file not from a .ppp file, the tracker information stored in the auto-generated .ppp file is set to the default
("localhost", 9999). If the tracker is listening from a different machine the tracker information in the .ppp file will need to be manually changed before the leecher
requests it.
