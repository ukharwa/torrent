import tkinter as tk
from tkinter import filedialog
<<<<<<< HEAD
import json
import generate_torrent as torrent
=======
import testfilespliting as torrent
>>>>>>> bb94a6652c37781c3a9a83cc2126c7318c3de243

# Create the main window
root = tk.Tk()
root.title("App")
root.geometry("500x700")  # Width x Height
<<<<<<< HEAD
label = tk.Label(root,text="PP Protocol", font=("Arial",14))
=======
label = tk.Label(root,text="Seeder", font=("Arial",14))
>>>>>>> bb94a6652c37781c3a9a83cc2126c7318c3de243
label.pack(pady=10)

def open_file():
    
<<<<<<< HEAD
    file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("PPP Files", "*.ppp"),))
  
    if file_path:
        print(f"Selected file: {file_path}")

        with open(file_path, "r") as file:
             data = json.load(file)

        text_box.insert(tk.END, data["info hash"]) 
    else:
            print("No file selected")

button = tk.Button(root,text="Seed a file",
                   font=("Helvetica",11),
                   bg= "green",
                   fg="white",
                   padx=5, pady=5,
                   relief="flat",
                   border=0,
                   command=open_file)
=======
    file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"),))
    
  
    if file_path:
        print(f"Selected file: {file_path}")
        torrent_data = torrent.gettorrentdata(file_path)
        print(torrent_data)
        text_box.insert(tk.END, torrent_data) 
    else:
            print("No file selected")

button = tk.Button(root,text="Seed a file",command=open_file)
>>>>>>> bb94a6652c37781c3a9a83cc2126c7318c3de243
button.pack(pady=5)
text_box = tk.Text(height=10,width=50)
text_box.pack(pady=10)

# Run the application
root.mainloop()
