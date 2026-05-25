import tkinter as tk

root = tk.Tk()

# Create Window
root.title("Tiktok Archiver")
root.geometry("500x300")
root.eval("tk::PlaceWindow . center")
root.resizable(False, False)
root.config(bg="red")

# Create Layout
frame = tk.Frame(root, width=500, height=300)
frame.pack(padx=10, pady=10)

root.mainloop()