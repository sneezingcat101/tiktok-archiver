import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from typing import Literal, Optional

##~~ GLOBAL VARIABLES ~~##
valid_urls = []
entered_urls = []
err = {}
seen = set()


##~~ FUNCTIONS ~~##
##~ URL Checks
#-- Pre-defined Error Messageboxes
def display_error(type: Literal["invalid", "duplicate", "incomplete"] = "invalid", index: int = None):
    if index is not None and type == "invalid":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL in line {index + 1}.") 
    elif type == "invalid":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL.")
        
    if index is not None and type == "incomplete":
        messagebox.showwarning(title="Warning", message=f"Incomplete Tiktok URL at line {index + 1}.") 
    elif type == "incomplete":
        messagebox.showwarning(title="Warning", message=f"Incomplete Tiktok URL.")
        
    if type == "duplicate":
        messagebox.showwarning(title="Warning", message=f"This URL is already in the list!")
    
#-- Rebuild URL link (remove garbage at the end)
def rebuild(url):
    parsed = urlparse(url)
    
    # return example: "https://www.tiktok.com/@btimbklm96485/video/7608125327763574029"
    return parsed.scheme + "://" + parsed.netloc + parsed.path

#-- Classify URL by parsing and then performing checks (returns "invalid", incomplete", and "valid" accordingly)
def classify_url(url):
    # urlparse returns tuple with scheme (https), netloc (www.tiktok.com), path (/@user/video/videoId), params, query, fragment
    parsed = urlparse(url)
    
    if parsed.scheme + "://" + parsed.netloc != "https://www.tiktok.com":
        return "invalid"
    
    path = parsed.path[1:].split("/")
    
    # Check link structure and if valid video URL
    if len(path) != 3 or "@" not in path[0] or path[1] not in ("video", "photo") or not path[2].isdigit():
        return "incomplete"
    
    return "valid"

#-- Clean up the pre-existing entries. Changes entered_urls for entries only in textbox.
def clean_entries():
    seen.clear()
    valid_urls.clear()
    entered_urls.clear()
    err.clear()

    # Get, check, and sort the URLs. 
    # Removes any duplicates, cleans white space and empty lines, ignores garbage
    for index, line in enumerate(url_entrybox.get(0.0, ctk.END).lower().splitlines()):
        status = classify_url(line.strip())
        
        if status == "valid": 
            line = rebuild(line)
            if line not in seen: 
                valid_urls.append(line)
                entered_urls.append(line)
            seen.add(line)
            
        if status == "incomplete":
            entered_urls.append(line)
            seen.add(line)
            if not err:
                err[len(entered_urls) - 1] = status
    
def update_textbox():
    url_entrybox.delete(0.0, ctk.END)
    url_entrybox.insert(0.0, "\n".join(entered_urls))
    
def add_URL():
    url = url_entryline.get()
    
    if not url:
        display_error()
        return
    
    status = classify_url(url)
    if status != "valid":
        display_error(status)
        return
    
    clean_entries()
    
    if rebuild(url) in seen:
        display_error("duplicate")
        return
    
    entered_urls.append(rebuild(url))
    update_textbox()
    
def download():
    clean_entries()
    
    update_textbox()
    
    if err:
        update_textbox()
        display_error(next(iter(err.values())), next(iter(err)))
        return
    
    # download starts below
    
    
    
    
##~ Button Functions
#-- Search for path
def browse_path():
    path = filedialog.askdirectory()
    if path:
        dir_entry.delete(0, ctk.END)
        dir_entry.insert(0, path)

#-- Clear the URLs Textbox
def clear_urls():
    response = messagebox.askyesno(title="Warning", message="Are you sure you would like to clear all URLs? This cannot be reverted.")
    if (response):
        url_entrybox.delete(0.0, ctk.END)

##~~ UI ~~##
root = ctk.CTk()

## Create Window
root.title("Tiktok Archiver")
root.geometry("500x300")
# opens in the center of screen
root.eval("tk::PlaceWindow . center")
root.resizable(False, False)
root.config(bg="black")

##~~ Create Layout
##~ Left
left_frame = ctk.CTkFrame(root, width=280, height=300, fg_color="white", border_width=1, border_color="black", corner_radius=0)
left_frame.pack(padx=1, pady=1, side=ctk.LEFT)
left_frame.pack_propagate(False)

##~ Right
right_frame = ctk.CTkFrame(root, width=220, height=300, fg_color="white", border_width=1, border_color="black", corner_radius=0)
right_frame.pack(pady=1, side=ctk.RIGHT)
right_frame.pack_propagate(False)

##~~ Top
##~ Top Left
#-- Top Left Frame
topleft_frame = ctk.CTkFrame(left_frame, height=30, border_width=1, fg_color="white", corner_radius=0)
topleft_frame.pack(fill="x", side=ctk.TOP,)
topleft_frame.pack_propagate(False)
topleft_lowerframe = ctk.CTkFrame(left_frame, height=30, border_width=1, border_color="black", fg_color="white", corner_radius=0)
topleft_lowerframe.pack(fill="x", side=ctk.TOP,)
topleft_lowerframe.pack_propagate(False)

#-- URL Textbox
url_entryline = ctk.CTkEntry(topleft_frame, width=230, text_color="black", fg_color="white", corner_radius=0, border_width=1, placeholder_text="Enter Video URL")
url_entryline.pack(pady=4, padx=(4,0),side=ctk.LEFT)

#-- "Add" Button
ctk.CTkButton(topleft_frame, border_width=1, text="Add", width=35, fg_color="white", text_color="black", corner_radius=0, command=add_URL).pack(pady=4, padx=(0,4), side=ctk.RIGHT)

#-- File Directory Textbox
dir_entry = ctk.CTkEntry(topleft_lowerframe, width=240, text_color="black", fg_color="white", corner_radius=0, border_width=1, placeholder_text="File directory")
dir_entry.pack(pady=4, padx=(4,0),side=ctk.LEFT)

#-- File Directory Selection Button
ctk.CTkButton(topleft_lowerframe, border_width=1, text="⋯", width=25, fg_color="white", text_color="black", corner_radius=0, font=("Arial", 30), command=browse_path).pack(pady=4, padx=(0,4), side=ctk.RIGHT)

##~ Top Right
#-- Top Right Frame
topright_frame = ctk.CTkFrame(right_frame, height=30, border_width=1, border_color="black", fg_color="white", corner_radius=0)
topright_frame.pack(fill="x", side=ctk.TOP,)
topright_frame.pack_propagate(False)

#-- Options Label
ctk.CTkLabel(topright_frame, text="Options", fg_color="transparent", text_color="black").pack(pady=1)

##~~ Content
##~ Left
#-- URLs Textbox
url_entrybox = ctk.CTkTextbox(left_frame, text_color="black", fg_color="white", corner_radius=0, border_width=1, font=("Arial", 10), wrap="none")
url_entrybox.pack(fill="x", side=ctk.TOP, padx=4, pady=4)
    
#-- Download Button
ctk.CTkButton(left_frame, border_width=1, text="Download", width=35, fg_color="white", text_color="black", corner_radius=0, command=download).pack(pady=(0,4), padx=(0,4), side=ctk.RIGHT)
ctk.CTkButton(left_frame, border_width=1, text="Clear", width=35, fg_color="white", text_color="black", corner_radius=0, command=clear_urls).pack(pady=(0,4), padx=(0,4), side=ctk.RIGHT)

##
root.mainloop()