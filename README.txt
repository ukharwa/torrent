
1. Download all the files
2. Run the tracker (see TRACKER section below)
3. Seed the file (see SEEDING section below)
4. Leech the file (see LEECHING section below)

TRACKER:
1. Run the file 'tracker.py'. This will ask you for an ip and a port to listen on. Defaults = ("localhost", 9999)

SEEDING:
	Run the file main.py. This will open up a gui with a select file button.
	Select a file you want to seed. This will generate a .ppp torrent file for the file you are seeding and begin seeding.
	If you already have a .ppp file and you have completed the download you can select the .ppp file and seed from there

LEECHING:
	Run main.py
	Click the "Select file" button
	Choose a .ppp file
	If a seeder is seeding that file your download will begin, otherwise try again later.

NOTES:
	When you are seeding a file not from a .ppp file, the tracker information stored in the auto-generated .ppp file is set to the default
	("localhost", 9999). If the tracker is listening from a different machine the tracker information in the .ppp file will need to be manually changed before the leecher
	requests it.
