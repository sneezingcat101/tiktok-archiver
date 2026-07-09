import yt_dlp
import os
from pathlib import Path
from win32com.client import Dispatch
from datetime import datetime
import requests, json, re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/148.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

_user_cache = {}

def extract_data(url: str):
    response = requests.get(url, headers=HEADERS, timeout=10)
    
    response.raise_for_status()
    
    data = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        response.text, re.DOTALL)
    if not data:
        return None
    
    return json.loads(data.group(1)).get('__DEFAULT_SCOPE__')

print(extract_data("https://www.tiktok.com/@cat7cc"))

def raws_folder(path) -> Path:
    if not path:
        return False
    
    folder_path = Path(path)
    
    if not folder_path:
        return False
    
    if folder_path.stem != "raw_files":
        folder_path.mkdir(parents=True, exist_ok=True)
    elif folder_path.stem == "raw_files":
        folder_path = folder_path.parent
        
    return folder_path

def create_shortcut(file_path, shortcut_path):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = file_path
    shortcut.WorkingDirectory = os.path.dirname(file_path)
    shortcut.save()

#-- Downloading using yt_dlp
def download_video(urls: list, path: str):
    
    # Create raws_files folder in path if it's not already there.
    path = raws_folder(path)
    
    if not path:
        return False
    
    # Download each URL
    for url in (urls):
        timestamp = f"{datetime.now():%Y-%m-%d_%H-%M-%S}"
        
        # Create folder for each video's raw files
        video_folder = path / "raw_files" / timestamp
        video_folder.mkdir(parents=True, exist_ok=True)
        
        options = {
            'format': 'best',
            'outtmpl': str(video_folder / f"{timestamp}.%(ext)s"),
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)   # download once
            video_path = ydl.prepare_filename(info)  
            
        print("video path")
        print(video_path)
        print(info)
        
        create_shortcut(str(video_folder / f"{video_path}"), str(path / f"{timestamp}.lnk"))
        
        write_metadata(info, video_folder, timestamp)

def write_metadata(info: dict, folder_path: str, timestamp: str):
    video = [
        f"Title: {info.get('title')}",
        f"Description: {info.get('description')}",
        f"Views: {info.get('view_count')}",
        f"Likes: {info.get('like_count')}",
        f"Saves: {info.get('save_count')}",
        f"Comments: {info.get('comment_count')}",
        f"Reposts: {info.get('repost_count')}",
    ]
    
    user = [
        f"Username: {info.get('uploader')}",
        f"Display Name: {info.get('channel')}",
        f"Followers: {info.get('title')}",
        f"Following: {info.get('title')}",
        f"Bio: {info.get('title')}",
    ]
    
    sound = [
        f"Sound Name: {info.get('track')}"
        f"Sound Creator: {info.get('artist')}"
    ]
    
    with open(folder_path / f"{timestamp}_info.txt", 'w', encoding='utf-8') as f:
        f.write("##~~ Video Information:\n" + f"\n##~ Video URL: {info.get('original_url')}\n#-- " + "\n#-- ".join(video) + "##~~ Uploader Information:\n" + f"\n##~ Uploader URL: {info.get('uploader_url')}\n#-- " + "\n#-- ".join(user) + "##~~ Sound Information:\n" + f"\n##~ Sound URL: {info.get('uploader_url')}\n#-- " + "\n#-- ".join(sound))

path = "C:/Users/neina/Desktop/Videos"

#download_video(["https://www.tiktok.com/@cat7cc/video/7619782378092776712"], path)