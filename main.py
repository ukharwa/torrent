from pathlib import Path
from tkinter import Tk, Canvas, Button, Text, Scrollbar,Label, filedialog,ttk
import tkinter as tk
from client import Client
import threading, logging
from src.create_cache import create_cache
from src.generate_torrent import filetotorrent
# list of torrent rows

class Row:
    def __init__(self, process, window, index):
        self.process = process
        self.window = window
        self.row_y = 80 + index * 30  # adjust Y position for new row
        self.name = process.get_name()
        self.status = process.get_status()
        self.filename_label = Label(window, text=self.name.split("/")[-1], font=("Arial", 12), anchor="w", width=30)
        self.status_label = Label(window, text=self.status, font=("Arial", 12), fg="green" if self.status == "Seeding..." else "red")
        self.progress_bar = ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")

    
    def place(self):
        self.filename_label.place(x=20, y=self.row_y)
        self.status_label.place(x=300, y=self.row_y)
        self.progress_bar.place(x=420, y=self.row_y)
    
    def update(self):
        self.progress_bar["value"] = self.process.get_percentage() * 100

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self.append, msg + "\n")

    def append(self, msg):
        self.text_widget.insert(tk.END, msg)
        self.text_widget.see(tk.END)

port = 9001

def main():
    torrent_rows = []

    
    

    # add the torrent row
    def add_torrent_row(process):
        row = Row(process, window, len(torrent_rows))

        return row  # Store row elements

    def open_file():
        file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"),))

        if not file_path:
            return  # If no file is selected, do nothing

        filename= file_path.split("/")[-1]
        if filename.split(".")[-1] != "ppp":
            filetotorrent(file_path, 2048, "192.168.79.129", 9999)
            filename = filename.split(".")[0] + ".ppp"
            create_cache(filename)
            

        
        
        log_text.insert(tk.END, f"Selected file: {file_path}\n")    #logging file path
        log_text.see(tk.END)  # scroll
        global port
        process = Client(filename, logger, port)
        port += 1
        threading.Thread(target=process.run, daemon=True).start()
        row = add_torrent_row(process)
        row.place()
        torrent_rows.append(row)
    
    def update_progress():
        for process in torrent_rows:
            process.update()
        window.after(10, update_progress)
    
    window = Tk()
    window.geometry("800x600")
    window.configure(bg="#FFFFFF")

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=600,
        width=800,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)


    # Header
    canvas.create_rectangle(0.0, 0.0, 800.0, 71.0, fill="#3E355A", outline="")
    canvas.create_text(15.0, 16.0, anchor="nw", text="PP Protocol", fill="#FFFFFF", font=("Arial", 24))

    # Logs label
    canvas.create_text(4.0, 302.0, anchor="nw", text="Logs:", fill="#000000", font=("Arial", 12))

    # Add a text box for logs
    
    log_text = Text(window, wrap="word", height=8, width=95, font=("Arial", 10))
    log_text.place(x=4, y=320, width=792, height=150)
    
    
    # Add a scrollbar for the logs
    scrollbar = Scrollbar(window, command=log_text.yview)
    scrollbar.place(x=780, y=320, height=150)
    log_text.config(yscrollcommand=scrollbar.set)

    # Button Styling
    button_width = 131
    button_height = 46
    spacing = 10  # space between buttons
    x_start = 10  # start position for first button
    y_position = 240  # y position for all buttons

    # Select Button
    select_button = Button(
        text="Select a file",
        font=("Trebuchet MS", 12),
        borderwidth=0,
        highlightthickness=0,
        command=open_file,
        relief="flat"
    )
    select_button.place(x=x_start, y=y_position, width=button_width, height=button_height)

    logger = logging.getLogger()  
    logger.setLevel(logging.INFO)  # Set your logging level

    text_handler = TextHandler(log_text)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    text_handler.setFormatter(formatter)

    logger.addHandler(text_handler)

    window.after(10, update_progress)
    window.resizable(False, False)
    window.mainloop()
    
main()
