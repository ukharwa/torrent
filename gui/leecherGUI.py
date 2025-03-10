import tkinter as tk

window = tk.Tk()

window.geometry("400x500")
window.title("PP Protocol: Leecher")

label = tk.Label(window, text="LEECHER", font=("Cascadia Code", 24))
label.pack(padx=30, pady=30)

# command/message display
textbox = tk.Text(window, font=("Cascadia Code", 18))
textbox.pack(padx=10, pady=10)

# buttons





window.mainloop()



