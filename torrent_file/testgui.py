import tkinter as tk
from tkinter import filedialog
import testfilespliting as torrent

# Create the main window
root = tk.Tk()
root.title("App")
root.geometry("500x700")  # Width x Height
label = tk.Label(root,text="Seeder", font=("Arial",14))
label.pack(pady=10)

def open_file():
    
    file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"),))
    
  
    if file_path:
        print(f"Selected file: {file_path}")
        torrent_data = torrent.gettorrentdata(file_path)
        print(torrent_data)
        text_box.insert(tk.END, torrent_data) 
    else:
            print("No file selected")

button = tk.Button(root,text="Seed a file",command=open_file)
button.pack(pady=5)
text_box = tk.Text(height=10,width=50)
text_box.pack(pady=10)

# Run the application
root.mainloop()
