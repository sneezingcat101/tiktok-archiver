import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from typing import Literal
from downloader import download
from pathlib import Path
import json
import atexit

##~~ GLOBAL VARIABLES ~~##
#-- URLS
valid_urls = []
entered_urls = []
seen = set()

#-- Error and the line
err = None
err_line = None

#-- Path
chosen_path = None

#-- Config
config_lines = []
config = {}

data = {}

##~~ FUNCTIONS ~~##
##~ Save/load functions
def load():
    global chosen_path, entered_urls, config_lines
    
    with open("save.json", "r") as file:
        save = json.load(file)
        
    if save.get('path'):
        chosen_path = save.get('path', "")
        update_path()
        
    if save.get('entered_urls'):
        entered_urls = save.get('entered_urls', [])
        update_textbox()
        
    if save.get('config'):
        config_lines = save.get('config', [])
    else:
        config_lines = ['##~~ Data to include in the download', "# true: Include | false: Don't include", '', '##~ Video', 'video file = true', '# title & description are often the same', 'title = false', 'description = true', 'views = false', 'likes = false', 'saves = false', 'comments = false', 'reposts = false', '', '##~ Creator', 'username = true', 'display name = false', 'followers = false', 'following = false', 'bio = false', '', '##~ Sound', 'sound file = false', 'name = false', 'creator = false']
    update_config()

def save():
    if chosen_path:
        data['path'] = chosen_path
        
    clean_entries()
    if entered_urls:
        data['entered_urls'] = entered_urls
        
    if config_lines:
        data['config'] = config_lines
    
    with open("save.json", "w") as file:
        json.dump(data, file, indent=2)

def on_close():
    save()
    root.destroy()

##~ URL-handling Functions
#-- Pre-defined Error Messageboxes
def display_error(type: Literal["invalid", "duplicate", "incomplete"] = "invalid", index: int = None):
    if index is not None and type == "invalid":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL in line {index + 1}.") 
    elif type == "invalid":
        messagebox.showwarning(title="Warning", message="Invalid Tiktok URL.")
        
    if index is not None and type == "incomplete":
        messagebox.showwarning(title="Warning", message=f"Incomplete Tiktok URL at line {index + 1}.") 
    elif type == "incomplete":
        messagebox.showwarning(title="Warning", message="Incomplete Tiktok URL.")
        
    if type == "duplicate":
        messagebox.showwarning(title="Warning", message="This URL is already in the list!")
        
    if type == "path":
        messagebox.showwarning(title="Warning", message="Invalid path!")
        
    if type == "empty":
        messagebox.showwarning(title="Warning", message="You have to enter a URL before the download can start!")
        
    if type == "config":
        messagebox.showwarning(title="Warning", message=f"Error in config at line {index + 1}.")
    
#-- Rebuild URL link (remove garbage at the end)
def rebuild(url) -> str:
    parsed = urlparse(url)
    
    # return example: "https://www.tiktok.com/@btimbklm96485/video/7608125327763574029"
    return parsed.scheme + "://" + parsed.netloc + parsed.path

#-- Classify URL by parsing and then performing checks (returns "invalid", incomplete", and "valid" accordingly)
def classify_url(url) -> str:
    # urlparse returns tuple with scheme (https), netloc (www.tiktok.com), path (/@user/video/videoId), params, query, fragment
    parsed = urlparse(url)
    
    # Check if valid Tiktok link
    if parsed.scheme + "://" + parsed.netloc != "https://www.tiktok.com":
        return "invalid"
    
    path = parsed.path[1:].split("/")
    
    # Check link structure and if valid video/photo URL
    if len(path) != 3 or "@" not in path[0] or path[1] not in ("video", "photo") or not path[2].isdigit():
        return "incomplete"
    
    return "valid"

#-- Clean up the pre-existing entries. Changes entered_urls for entries only in textbox.
def clean_entries():
    global err, err_line
    
    # Clean up global functions
    seen.clear()
    valid_urls.clear()
    entered_urls.clear()
    err = None
    err_line = None

    # Get, check, and sort the URLs. 
    # Removes any duplicates, cleans white space and empty lines, ignores garbage
    for line in url_entrybox.get(0.0, ctk.END).lower().splitlines():
        status = classify_url(line.strip())
        
        # Add to global lists if status returns valid
        if status == "valid": 
            line = rebuild(line)
            if line not in seen: 
                valid_urls.append(line)
                entered_urls.append(line)
            seen.add(line)
        
        # Add only to entered_urls and the first error is marked
        if status == "incomplete":
            entered_urls.append(line)
            seen.add(line)
            if not err:
                err = status
                err_line = len(entered_urls) - 1

##~ Config Functions
#--
def parse_config() -> bool:
    global err, err_line
    
    raw_config = configs_box.get(0.0, ctk.END).splitlines()
    
    for index, line in enumerate(raw_config):
        line = line.lower().strip()
        
        if line.startswith("#") or line == "":
            continue
        
        if '=' not in line:
            err = "config"
            err_line = index
            return False
        
        key, value = line[:line.index('=')].strip(), line[line.index("=") + 1:].strip()

        config[key] = value == "true"
        
    return True

##~ Button Functions
#-- Function for the 'add' button of the single line URL entry
def add_URL():
    url = url_entryline.get()
    
    # Check if entry is empty
    if not url:
        display_error()
        return
    
    # Check if entry is a URL
    status = classify_url(url)
    if status != "valid":
        display_error(status)
        return
    
    clean_entries()
    
    # Rebuild URL and check for duplicates
    if rebuild(url) in seen:
        display_error("duplicate")
        return
    
    # Add newly cleaned URL to the global list and update the URLs Textbox
    entered_urls.append(rebuild(url))
    update_textbox()

#-- Function for the 'download' button to begin the process of downloading off the list
def start_download():
    # Clean URLs and update the Textbox for the errors to display correctly and cleanly
    clean_entries()
    update_textbox()
    
    # Popup error if an unfinished link is found.
    if err:
        update_textbox()
        display_error(err, err_line)
        return
    
    # Check if valid path or if empty
    save_path()
    if not chosen_path:
        display_error("path")
        return
        
    # Return if valid_urls empty
    if not valid_urls:
        display_error("empty")
        return
    
    if parse_config() == False:
        display_error(err, err_line)
        return

    # download starts below
    download(valid_urls, chosen_path, config)

#-- Search for path
def browse_path():
    global chosen_path
    chosen_path = filedialog.askdirectory()
    
    update_path()
    save_path()

def save_path():
    global chosen_path
    
    if not dir_entry.get():
        return
    
    path = Path(dir_entry.get())
    
    if path.exists() and path.is_dir():
        chosen_path = str(path)
        
    
#-- Clear the URLs Textbox
def clear_urls():
    response = messagebox.askyesno(title="Warning", message="Are you sure you would like to clear all URLs? This cannot be reverted.")
    if (response):
        url_entrybox.delete(0.0, ctk.END)
        
##~ UI-related Functions
#-- Update the textbox with the most recent clean URLs
def update_textbox():
    url_entrybox.delete(0.0, ctk.END)
    url_entrybox.insert(0.0, "\n".join(entered_urls))
    
def update_path():
    dir_entry.delete(0, ctk.END)
    dir_entry.insert(0, chosen_path)

def update_config():
    configs_box.delete(0.0, ctk.END)
    configs_box.insert(0.0, "\n".join(config_lines))

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
    
#-- Download/Clear Buttons
ctk.CTkButton(left_frame, border_width=1, text="Download", width=35, fg_color="white", text_color="black", corner_radius=0, command=start_download).pack(pady=(0,4), padx=(0,4), side=ctk.RIGHT)
ctk.CTkButton(left_frame, border_width=1, text="Clear", width=35, fg_color="white", text_color="black", corner_radius=0, command=clear_urls).pack(pady=(0,4), padx=(0,4), side=ctk.RIGHT)

##~ Right
#-- Toggles
configs_box = ctk.CTkTextbox(right_frame, text_color="black", fg_color="white", corner_radius=0, border_width=1, font=("Arial", 10), wrap="none", height=230)
configs_box.pack(fill="x", side=ctk.TOP, padx=4, pady=4)

#-- Save/Reset config Buttons
ctk.CTkButton(right_frame, border_width=1, text="Reset", width=35, fg_color="white", text_color="black", corner_radius=0).pack(pady=(0,4), padx=(0,4), side=ctk.RIGHT)

##
load()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()