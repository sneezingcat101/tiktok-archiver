import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from typing import Literal, Optional

##~~ FUNCTIONS ~~##
##~ URL Checks
#-- Parse URL and check if valid Tiktok Video then rebuild URL
def rebuild_url(url: str, index: Optional[int] = None, showError: bool = False, is_batch: bool = False):
    # urlparse returns tuple with scheme (https), netloc (www.tiktok.com), path (/@user/video/videoId), params, query, fragment
    parsed = urlparse(url)
        
    # Check if valid tiktok link (always drops garbage)
    if parsed.scheme + "://" + parsed.netloc != "https://www.tiktok.com":
        if showError: bad_url(index = index)
        return (None, False)
 
    # Check link structure and if valid video URL
    path = parsed.path[1:].split("/")
    
    ## Checks, maintain incomplete URL to help keep track of links
    # has valid link structure
    if len(path) != 3:
        if showError: bad_url("incompleteURL", index)
        return (url, False) if is_batch else (None, False)
    # has username
    if "@" not in path[0]:
        if showError: bad_url("incompleteURL", index)
        return (url, False) if is_batch else (None, False)
    # has 'video'
    if "video" not in path[1]:
        if showError: bad_url("notVideo", index)
        return (url, False) if is_batch else (None, False)
    # has videoID
    if not path[2].isdigit():
        if showError: bad_url("incompleteURL", index)
        return (url, False) if is_batch else (None, False)
    # rebuild new URL
    return parsed.scheme + "://" + parsed.netloc + parsed.path, True
    
#-- Error Messageboxes
def bad_url(type: Literal["badURL", "notVideo", "dupe", "incompleteURL"] = "badURL", index: Optional[int] = None):
    if index is not None and type == "badURL":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL in line {index + 1}.") 
    elif type == "badURL":
        messagebox.showwarning(title="Warning", message=f"Invalid Tiktok URL.")
        
    if index is not None and type == "incompleteURL":
        messagebox.showwarning(title="Warning", message=f"Incomplete Tiktok URL at line {index + 1}.") 
    elif type == "incompleteURL":
        messagebox.showwarning(title="Warning", message=f"Incomplete Tiktok URL.")
    
    if index is not None and type == "notVideo":
        messagebox.showwarning(title="Warning", message=f"URL in line {index + 1} does not link to a valid video.") 
    elif type == "notVideo":
        messagebox.showwarning(title="Warning", message=f"URL does not link to a valid video.")
    
    if type == "dupe":
        messagebox.showwarning(title="Warning", message=f"This URL is already in the list!")

#-- Check validity of URLs, rewrite textboxes, remove duplicates (returns reformatted URLs list)
def check_URLs(raw_url: Optional[str] = None):
    valid = True
    seen = set()
    urls = []
    
    # Get and rebuild the URLs already in textBox 'urls' list and 'seen' set().
    for index, line in enumerate(url_entrybox.get(0.0, ctk.END).lower().splitlines()):
        line, ok = rebuild_url(line.strip(), None if raw_url else index, False if raw_url else True, False if raw_url else True)
        if line: 
            if line not in seen: urls.append(line)
            seen.add(line)
        if not ok: valid = False
    
    # Logic below runs only if adding via 'add' button
    if raw_url:
        added_url, _ = rebuild_url(raw_url, showError=True, is_batch=False)
    else:
        added_url = None
    
    if added_url and added_url not in seen:
        urls.append(added_url)
        clean_urls(urls)
        return None
    elif added_url and added_url in seen:
        bad_url(type="dupe")
        clean_urls(urls)
        return None
    elif added_url:
        clean_urls(urls)
        return None
    
    return urls if valid == True else None

##~ URL Adding Functions
#-- Add Video URL to URLs Textbox
def add_URL():
    if not url_entryline.get():
        bad_url(type="badURL")
    else:
        check_URLs(url_entryline.get())

#-- Search for path
def browse_path():
    path = filedialog.askdirectory()
    if path:
        dir_entry.delete(0, ctk.END)
        dir_entry.insert(0, path)
        
##~ Download Functions
#-- Prepare download and start
def download():
    # Check URLs
    urls = check_URLs()
    
    # Download each video
    if urls:
        # Placeholder
        print()

##~ Cleaning Functions
#-- Clear the URLs Textbox
def clear_urls():
    response = messagebox.askyesno(title="Warning", message="Are you sure you would like to clear all URLs? This cannot be reverted.")
    if (response):
        url_entrybox.delete(0.0, ctk.END)
        
#-- Clean up Textbox duplicates and URL formatting before downloads
def clean_urls(urls):
    # Replace textbox URLs with clean ones
    formatted_urls = "\n".join(urls)
    url_entrybox.delete(0.0, ctk.END)
    url_entrybox.insert(0.0, formatted_urls)

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