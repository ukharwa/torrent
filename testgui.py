import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
import json

def gui():
    # Create the main window
    root = tk.Tk()
    root.title("App")
    root.geometry("500x700")  # Width x Height
    label = tk.Label(root, text="PP Protocol", font=("Arial", 14))
    label.pack(pady=10)

    def open_file():
        global file_path
        file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("PPP Files", "*.ppp"),))
    
        if file_path:
            print(f"Selected file: {file_path}")

            with open(file_path, "r") as file:
                data = json.load(file)

            text_box.insert(tk.END, data["info hash"]) 
        else:
            print("No file selected")

    # Frame to hold buttons horizontally
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    upload_button = tk.Button(button_frame, text="Upload torrent file",
                            font=("Helvetica", 11),
                            bg="#2d9407", fg="white",
                            padx=5, pady=5,
                            relief="flat",
                            activebackground="green",
                            activeforeground="white",
                            border=0,
                            command=open_file)
    upload_button.pack(side=tk.LEFT, padx=5)  # Place to the left

    cancel_button = tk.Button(button_frame, text="Cancel",
                            font=("Helvetica", 11),
                            bg="#d60202", fg="white",
                            padx=5, pady=5,
                            relief="flat",
                            activebackground="#a10303",
                            activeforeground="white",
                            border=0)
    cancel_button.pack(side=tk.LEFT, padx=5)  # Place next to upload button

    text_box = tk.Text(root, height=10, width=50)
    text_box.pack(pady=10)

    # Run the application
    root.mainloop()
    return file_path

