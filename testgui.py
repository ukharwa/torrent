import tkinter as tk
from tkinter import filedialog
import json
import generate_torrent as torrent

# Create the main window
root = tk.Tk()
root.title("App")
root.geometry("500x700")  # Width x Height
label = tk.Label(root,text="PP Protocol", font=("Arial",14))
label.pack(pady=10)

def open_file():
    
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
button.pack(pady=5)
text_box = tk.Text(height=10,width=50)
text_box.pack(pady=10)

# Run the application
root.mainloop()
