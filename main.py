
from tkinter import Tk, Canvas, Button, Text, Scrollbar,Label, filedialog,ttk
import tkinter as tk
from src.client import Client
import threading, logging
from src.create_cache import create_cache
from src.generate_torrent import filetotorrent

class Row:
    def __init__(self, process, window, index):
        self.process = process
        self.window = window
        self.row_y = 80 + index * 30  # adjust Y position for new row
        self.name = process.get_name()
        self.filename_label = Label(window, text=self.name.split("/")[-1], font=("Arial", 12), anchor="w", width=30)
        self.status_label = Label(window,  font=("Arial", 12), )
        self.update_status()
        self.progress_bar = ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")

    
    def place(self):
        self.filename_label.place(x=20, y=self.row_y)
        self.status_label.place(x=300, y=self.row_y)
        self.progress_bar.place(x=420, y=self.row_y)
    
    def progress(self):
        self.progress_bar["value"] = self.process.get_percentage() * 100
        if self.process.get_status() == 0:
            self.status = "Seeding..."
        else:
            self.status = "Leeching..."

    def update_status(self):
        self.status = self.process.get_status()
        self.status_label.config(text="Seeding..." if self.status == 0 else "Leeching...")
        self.status_label.config(fg="green" if self.status == 0 else "red")

    def update(self):
        self.progress()
        self.update_status()


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
    processes = []

    # add the torrent row
    def add_torrent_row(process):
        row = Row(process, window, len(processes))

        return row  # store row elements

    def open_file():

        file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"),))
        log_text.insert(tk.END, f"Selected file: {file_path}\n")    #logging file path
        log_text.see(tk.END)  # scroll

        if not file_path:
            return  # if no file selected => do nothing

        filename= file_path.split("/")[-1]

        if filename.split(".")[-1] != "ppp":
            filename = filename.split(".")[0] + ".ppp"

            def new_torrent(torrent, path):
                filetotorrent(path)
                create_cache(torrent, path)

            logger.info("Generating torrent (.ppp) file for requested file")
            thread = threading.Thread(target=new_torrent, args=(filename, file_path,), daemon=True)
            thread.start()
            thread.join()

        global port
        process = Client(filename, logger, port)
        port += 1
        threading.Thread(target=process.run, daemon=True).start()
        row = add_torrent_row(process)
        row.place()
        processes.append(row)
    
    def update_progress():
        for process in processes:
            process.update()
        window.after(10, update_progress)
    
    window = Tk()
    window.geometry("800x510")
    window.configure(bg="#FFFFFF")

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=500,
        width=800,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)


    #header
    canvas.create_rectangle(0.0, 0.0, 800.0, 71.0, fill="#3E355A", outline="")
    canvas.create_text(15.0, 16.0, anchor="nw", text="PP Protocol", fill="#FFFFFF", font=("Arial", 24))

    # logs label
    canvas.create_text(4.0, 322.0, anchor="nw", text="Logs:", fill="#000000", font=("Arial", 12))

    # add a text box for logs
    
    log_text = Text(window, wrap="word", height=8, width=95, font=("Arial", 10))
    log_text.place(x=4, y=345, width=792, height=150)
    
    
    # add a scrollbar for the logs
    scrollbar = Scrollbar(window, command=log_text.yview)
    scrollbar.place(x=780, y=345, height=150)
    log_text.config(yscrollcommand=scrollbar.set)

    # button styling
    button_width = 780
    button_height = 46
    x_start = 10  # start position for first button
    y_position = 270  # y position for all buttons

    select_button = Button(
        text="Select a file",
        font=("Arial", 12),
        borderwidth=0,
        highlightthickness=0,
        command=open_file,
        relief="flat",
        bg="#d4d4d4"  
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
