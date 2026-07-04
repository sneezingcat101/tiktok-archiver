import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox

root = ctk.CTk()

## Create Window
root.title("Tiktok Archiver")
root.geometry("500x300")
# opens in the center of screen
root.eval("tk::PlaceWindow . center")
root.resizable(False, False)
root.config(bg="black")

## Create Layout
left_frame = ctk.CTkFrame(root, width=280, height=300, fg_color="white", border_width=1, border_color="black", corner_radius=0)
left_frame.pack(padx=1, pady=1, side=ctk.LEFT)
left_frame.pack_propagate(False)

right_frame = ctk.CTkFrame(root, width=220, height=300, fg_color="white", border_width=1, border_color="black", corner_radius=0)
right_frame.pack(pady=1, side=ctk.RIGHT)
right_frame.pack_propagate(False)

## Top
#-- Top Left
topleft_frame = ctk.CTkFrame(left_frame, height=30, border_width=1, fg_color="white", corner_radius=0)
topleft_frame.pack(fill="x", side=ctk.TOP,)
topleft_frame.pack_propagate(False)
topleft_lowerframe = ctk.CTkFrame(left_frame, height=30, border_width=1, border_color="black", fg_color="white", corner_radius=0)
topleft_lowerframe.pack(fill="x", side=ctk.TOP,)
topleft_lowerframe.pack_propagate(False)

# URL Textbox
ctk.CTkEntry(topleft_frame, width=230, text_color="black", fg_color="white", corner_radius=0, border_width=1, placeholder_text="Enter Video URL").pack(pady=4, padx=(4,0),side=ctk.LEFT)

# "Add" Button
ctk.CTkButton(topleft_frame, border_width=1, text="Add", width=35, fg_color="white", text_color="black", corner_radius=0).pack(pady=4, padx=(0,4), side=ctk.RIGHT)

# File Directory Textbox
dir_entry = ctk.CTkEntry(topleft_lowerframe, width=240, text_color="black", fg_color="white", corner_radius=0, border_width=1, placeholder_text="File directory")
dir_entry.pack(pady=4, padx=(4,0),side=ctk.LEFT)

# Search for path
def browse_path():
    path = filedialog.askdirectory()
    if path:
        dir_entry.delete(0.0, ctk.END)
        dir_entry.insert(0.0, path)

# File Directory Selection Button
ctk.CTkButton(topleft_lowerframe, border_width=1, text="⋯", width=25, fg_color="white", text_color="black", corner_radius=0, font=("Arial", 30), command=browse_path).pack(pady=4, padx=(0,4), side=ctk.RIGHT)

#-- Top Right
topright_frame = ctk.CTkFrame(right_frame, height=30, border_width=1, border_color="black", fg_color="white", corner_radius=0)
topright_frame.pack(fill="x", side=ctk.TOP,)
topright_frame.pack_propagate(False)

# Options Label
ctk.CTkLabel(topright_frame, text="Options", fg_color="transparent", text_color="black").pack(pady=1)

## Content
#-- Left

# URLs Textbox
url_entry = ctk.CTkTextbox(left_frame, text_color="black", fg_color="white", corner_radius=0, border_width=1, font=("Arial", 10), wrap="none")
url_entry.pack(fill="x", side=ctk.TOP, padx=4, pady=4)

# Clear the URLs Textbox
def clear_urls():
    response = messagebox.askyesno(title="Warning", message="Are you sure you would like to clear all URLs? This cannot be reverted.")
    if (response):
        url_entry.delete(0.0, ctk.END)
        
def prepare_urls():
    # Grab the raw text and split each line into items of URLs list
    urls = url_entry.get(0.0, ctk.END).lower().splitlines()
    for index, url in enumerate(urls):
        # Check if valid tiktok link
        if url[0:24] != "https://www.tiktok.com/@":
            messagebox.showwarning(title="Warning", message=f"Invalid URL in line {index + 1}.")
            
        # Check if valid video
        if "video" not in url:
            messagebox.showwarning(title="Warning", message=f"Entry in line {index + 1} is not a valid video.")
            
            

# Download Button
ctk.CTkButton(left_frame, border_width=1, text="Download", width=35, fg_color="white", text_color="black", corner_radius=0, command=prepare_urls).pack(pady=4, padx=(0,4), side=ctk.RIGHT)
ctk.CTkButton(left_frame, border_width=1, text="Clear", width=35, fg_color="white", text_color="black", corner_radius=0, command=clear_urls).pack(pady=4, padx=(0,4), side=ctk.RIGHT)

##
root.mainloop()