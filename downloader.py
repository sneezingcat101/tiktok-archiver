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

def extract_data(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=20)
    
    response.raise_for_status()
    
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        response.text, re.DOTALL)
    if not match:
        return None
    
    return json.loads(match.group(1)).get('__DEFAULT_SCOPE__')

def parse_data(creator_data: dict, video_data: dict) -> dict:
    parsed_data = {}
    
    sound = video_data.get('webapp.video-detail').get('itemInfo').get('itemStruct').get('music')
    
    user_info = creator_data.get('webapp.user-detail').get('userInfo')
    profile = user_info.get('user')
    user_stats = user_info.get('statsV2')
    
    # creator data
    # follows
    if user_stats.get('followerCount'):
        parsed_data['follower_count'] = user_stats.get('followerCount')
    else:
        parsed_data['follower_count'] = 'NoResultFound'
        
    if user_stats.get('followingCount'):
        parsed_data['following_count'] = user_stats.get('followingCount')
    else:
        parsed_data['following_count'] = 'NoResultFound'
        
    # bio
    if profile.get('signature'):
        parsed_data['bio'] = profile.get('signature')
    else:
        parsed_data['bio'] = 'NoResultFound'
        
    # sound urls
    # raw sound download url (to combat sounds url changes name changes)
    if sound.get('playUrl'):
        parsed_data['raw_sound_url'] = sound.get('playUrl').replace(r"\u00", "/")
    else:
        parsed_data['raw_sound_url'] = 'NoResultFound'
    
    # normal sound url
    if sound.get('id') and sound.get('title'):
        parsed_data['sound_url'] = "https://www.tiktok.com/music/" + sound.get('title').replace(" ", "-") + sound.get('id')
    else:
        parsed_data['sound_url'] = 'NoResultFound'
        
    return parsed_data
    
        
    

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
        
        create_shortcut(str(video_folder / f"{video_path}"), str(path / f"{timestamp}.lnk"))
        
        write_metadata(info, video_folder, timestamp)

def write_metadata(info: dict, folder_path: str, timestamp: str):
    video_url = info.get('original_url')
    creator_url = info.get('uploader_url')
    
    creator_data = None
    video_data = None
    
    retrieved = None
    
    if video_url and creator_url:
        video_data = extract_data(video_url)
        creator_data = extract_data(creator_url)
        
        retrieved = parse_data(creator_data, video_data)
        
    
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
        f"Followers: {retrieved.get('follower_count')}",
        f"Following: {retrieved.get('following_count')}",
        f"Bio: \n{retrieved.get('bio')}",
    ]
    
    sound = [
        f"Sound Name: {info.get('track')}",
        f"Sound Creator: {info.get('artist')}"
    ]
    
    with open(folder_path / f"{timestamp}_info.txt", 'w', encoding='utf-8') as f:
        f.write("##~~ Video Information:\n" + f"\n##~ Video URL: {video_url}\n#-- " + "\n#-- ".join(video) + "\n\n##~~ Uploader Information:\n" + f"\n##~ Uploader URL: {creator_url}\n#-- " + "\n#-- ".join(user) + "\n\n##~~ Sound Information:\n" + f"\n##~ Sound URL: {retrieved.get('sound_url')}\n##~ Raw Sound URL: {retrieved.get('raw_sound_url')}\n#-- " + "\n#-- ".join(sound))

path = "C:/Users/neina/Desktop/Videos"

download_video(["https://www.tiktok.com/@cat7cc/video/7627600991268998407"], path)