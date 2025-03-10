import tkinter as tk
from tkinter import filedialog
import testfilespliting as torrent

# Create the main window
root = tk.Tk()
root.title("My First Tkinter App")
root.geometry("500x700")  # Width x Height
label = tk.Label(root,text="Seeder", font=("Arial",14))
label.pack(pady=10)

def open_file():
    
    file_path = filedialog.askopenfilename(title="Select a File",
                                           filetypes=[("All Files", "*.*"))
    
    print(file_path)
    if file_path:  # If a file is selected
        torrent_data = torrent.filetotorrent(file_path)
        print(torrent_data)
        text_box.insert(tk.END, torrent_data)  # Display content in text widget


button = tk.Button(root,text="Seed a file",command=open_file)
button.pack(pady=5)
text_box = tk.Text(height=10,width=50)
text_box.pack(pady=10)

# Run the application
root.mainloop()
