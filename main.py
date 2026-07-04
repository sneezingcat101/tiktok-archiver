import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from typing import Literal, Optional

##~~ FUNCTIONS ~~##
##~ URL Checks
#-- Error Messageboxes
def bad_url(is_list: bool = False, index: Optional[int] = None, type: Literal["badURL", "notVideo", "dupe"] = "badURL"):
    if is_list and type == "badURL":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL in line {index + 1}.") 
    elif type == "badURL":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL.")
    
    if is_list and type == "notVideo":
        messagebox.showwarning(title="Warning", message=f"URL in line {index + 1} does not link to a valid video.") 
    elif type == "notVideo":
        messagebox.showwarning(title="Warning", message=f"URL does not link to a valid video.")
    
    if type == "dupe":
        messagebox.showwarning(title="Warning", message=f"This URL is already in the list!")

#-- Check validity of URL
def check_URLs(raw_url: ctk.CTkEntry, is_list: bool = False):
    # Grab the raw URLs string and split lines into list
    raw_urls = raw_url.get().lower()
    split_urls = raw_urls.splitlines()
    dupes = set(url_entrybox.get(0.0, ctk.END).splitlines())
    urls = []
    
    ## URL Checks
    for index, url in enumerate(split_urls):
        # urlparse returns tuple with scheme (https), netloc (www.tiktok.com), path (/@user/video/videoId), params, query, fragment
        parsed = urlparse(url)
        
        # Check if valid tiktok link
        if parsed.scheme + "://" + parsed.netloc != "https://www.tiktok.com":
            bad_url(is_list, index)
            return
            
        # Check link structure and if valid video URL
        path = parsed.path[1:-1].split("/")
        # has username
        if "@" not in path[0]:
            bad_url(is_list, index)
            return
        # has 'video'
        if "video" not in path[1]:
            bad_url(is_list, index, "notVideo")
            return
        # has videoID
        if not path[2].isdigit():
            bad_url(is_list, index)
            return
        
        # Check duplicates for entry adding
        if not is_list and parsed.scheme + "://" + parsed.netloc + parsed.path in dupes:
            bad_url(type="dupe")
            return
        
        # Rebuild URL and append to new list
        urls.append(parsed.scheme + "://" + parsed.netloc + parsed.path)
        
    # Returns either a list or a string
    return urls if is_list else urls[0]


##~ URL Adding Functions
#-- Add Video URL to URLs Textbox
def add_URL():
    url = check_URLs(url_entryline)
    
    # Insert the URL with a newline. If no previous newline, one is added.
    if url:
        url_entrybox.insert(0.0, url + "\n" if (url_entrybox.get(0.0, ctk.END))[-1:-3] or url_entrybox.get(0.0, ctk.END) else "\n" + url + "\n")

#-- Search for path
def browse_path():
    path = filedialog.askdirectory()
    if path:
        dir_entry.delete(0, ctk.END)
        dir_entry.insert(0, path)
        
##~ Download Functions
#-- Prepare download and start
def download():
    urls = check_URLs(url_entrybox, False)
    
    # Download each video

##~ Cleaning Functions
#-- Clear the URLs Textbox
def clear_urls():
    response = messagebox.askyesno(title="Warning", message="Are you sure you would like to clear all URLs? This cannot be reverted.")
    if (response):
        url_entrybox.delete(0.0, ctk.END)
        
#-- Check for duplicate URLs and clean up URLs before downloading
def clean_urls(urls):
    print()

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