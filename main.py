from pathlib import Path
from tkinter import Tk, Canvas, Button, Text, Scrollbar,Label, filedialog,ttk
import tkinter as tk
import client
import socket
# list of torrent rows
torrent_rows = []

def main():
    global log_text    
    # add the torrent row
    def add_torrent_row(filename, status):
        # adds row with filename, status, and progress bar
        row_y = 80 + len(torrent_rows) * 30  # adjust Y position for new row

        filename_label = Label(window, text=filename.split("/")[-1], font=("Arial", 12), anchor="w", width=30)
        filename_label.place(x=20, y=row_y)

        status_label = Label(window, text=status, font=("Arial", 12), fg="green" if status == "Seeding" else "red")
        status_label.place(x=300, y=row_y)
#########################################progress bar#####################################################################
        progress = ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")
        progress.place(x=420, y=row_y)
        progress["value"] = 50  #######################################

        torrent_rows.append((filename_label, status_label, progress))  # Store row elements



    def open_file():
        file_path = filedialog.askopenfilename(title="Select A File", filetypes=(("PPP Files", "*.ppp"),))
        filename= file_path.split("/")[-1]

        if not file_path:
            return  # If no file is selected, do nothing
        

        log_text.insert(tk.END, f"Selected file: {file_path}\n")    #logging file path
        log_text.see(tk.END)  # scroll

        torrent_info = client.read_torrent_file(file_path)          #reading the file contents
        cache = client.check_cache(torrent_info)                    #checking if peer has this file cached if not they are leeching else they seeding
        client_port = 9991

        downloaded = cache["downloaded"]
        uploaded = cache["uploaded"]
        left = cache["left"]

        response = client.connect_to_tracker(              #sending connection resquest to tracker
            tuple(torrent_info["tracker"]),
            torrent_info["info hash"],
            downloaded, uploaded, left,
            socket.gethostbyname(socket.gethostname()), client_port, 
            log_text
        )


        if cache["left"] == 0:                          #if the peer has nothing left to download then it is assumed they are seeding
            log_text.insert(tk.END, "Seeding...\n")
            status = "Seeding"
            client.seed(torrent_info, cache, 9001)
        else:                                           #if the peer still has missing pieces then they leech
            log_text.insert(tk.END, "Leeching...\n")
            status = "Leeching"
            client.leech(torrent_info, cache, response)

        add_torrent_row(filename, status)
        
        log_text.see(tk.END)  # Auto-scroll

            

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

    # Upload Button
    upload_button = Button(
        text="Upload",
        font=("Trebuchet MS", 12),
        borderwidth=0,
        highlightthickness=0,
        command=open_file,
        relief="flat"
    )
    upload_button.place(x=x_start + button_width + spacing, y=y_position, width=button_width, height=button_height)

    add_torrent_row("/bruh.png", "leeching")
    add_torrent_row("/bruh.png", "leeching")
    add_torrent_row("/bruh.png", "leeching")
    # Cancel Button
    cancel_button = Button(
        text="Cancel",
        font=("Trebuchet MS", 12),
        borderwidth=0,
        highlightthickness=0,
        command=open_file,
        relief="flat"
    )
    cancel_button.place(x=x_start + 2 * (button_width + spacing), y=y_position, width=button_width, height=button_height)

    window.resizable(False, False)
    window.mainloop()

main()
