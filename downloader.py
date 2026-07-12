from pathlib import Path
from win32com.client import Dispatch
from datetime import datetime
import requests, json, re, yt_dlp, os

#-- Metadata to be sent in the request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/148.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

#-- Function to send a request to given URL and scrape '__UNIVERSAL_DATA_FOR_REHYDRATION__'
# For arg. either send a user profile URL or a content URL
def extract_data(url: str) -> dict:
    # Send initial request
    response = requests.get(url, headers=HEADERS, timeout=20)
    
    # Raise error if one is given
    response.raise_for_status()
    
    # Find the entire '__UNIVERSAL_DATA_FOR_REHYDRATION__' line and filter html tags
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        response.text, re.DOTALL)
    if not match:
        return None
    
    # Return the match w/o html tags as a dict
    return json.loads(match.group(1)).get('__DEFAULT_SCOPE__')

#-- Filter the scraped data and find variables needed
# For arg. send in user profile data and content data
def parse_data(creator_data: dict, video_data: dict) -> dict:
    parsed_data = {}
    
    # Reference to the sound data in the dict
    sound = video_data.get('webapp.video-detail').get('itemInfo').get('itemStruct').get('music')
    
    # References to user branches
    user_info = creator_data.get('webapp.user-detail').get('userInfo')
    profile = user_info.get('user')
    user_stats = user_info.get('statsV2')
    
    # creator data
    # follows
    if user_stats.get('followerCount'):
        parsed_data['followers'] = user_stats.get('followerCount')
    else:
        parsed_data['followers'] = 'NoResultFound'
        
    if user_stats.get('followingCount'):
        parsed_data['following'] = user_stats.get('followingCount')
    else:
        parsed_data['following'] = 'NoResultFound'
    
    # names
    if profile.get('uniqueId'):
        parsed_data['username'] = profile.get('uniqueId')
    else:
        parsed_data['username'] = 'NoResultFound'
    
    # bio
    if profile.get('nickname'):
        parsed_data['display_name'] = profile.get('nickname')
    else:
        parsed_data['display_name'] = 'NoResultFound'
        
    # sound urls
    # raw sound download url (backup incase name changes cause url changes)
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

#-- Create a folder where the raw video and metadata will be stored
def raws_folder(path) -> Path:
    if not path:
        return False
    
    folder_path = Path(path)
    
    if not folder_path:
        return False
    
    # If no raw_files folder exists in the directory, create one
    if folder_path.stem != "raw_files":
        folder_path.mkdir(parents=True, exist_ok=True)
    # If the directory given is to the raw_files folder itself, redefine the folder_path as the parent folder
    elif folder_path.stem == "raw_files":
        folder_path = folder_path.parent
        
    return folder_path

#-- Create a shortcut to the raw video with the same name
# This will make it easier to find what video you're looking for, rather than sort through numerous folders
def create_shortcut(file_path, shortcut_path):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = file_path
    shortcut.WorkingDirectory = os.path.dirname(file_path)
    shortcut.save()

#-- Formatting helper for the metadata text file
def section(header, urls, items):
    lines = [f"##~~ {header}: ", ""]
    
    # Incase of multiple URLs
    lines += [f'#~ {u}' for u in urls]
    
    lines += [f'#-- {i}' for i in items if i is not None]
    
    return "\n".join(lines)

#-- Downloading using yt_dlp
def download(urls: list, current_path: str, config: dict):
    
    # Create raws_files folder in path if it's not already there.
    # raws_folder returns parsed ver. of path and creates a raws_folder
    current_path = raws_folder(current_path)
    
    if not current_path:
        return False
    
    # Download each URL
    for url in (urls):
        timestamp = f"{datetime.now():%Y-%m-%d_%H-%M-%S}"
        
        # Create folder for each video's raw files
        video_folder = current_path / "raw_files" / timestamp
        video_folder.mkdir(parents=True, exist_ok=True)
        
        # Create the file named as the current time of download
        options = {
            'format': 'best',
            'outtmpl': str(video_folder / f"{timestamp}.%(ext)s"),
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)  
        
        create_shortcut(str(video_folder / f"{video_path}"), str(current_path / f"{timestamp}.lnk"))
        
        write_metadata(info, video_folder, timestamp, config)

#-- Create the file containing the metadata
def write_metadata(info: dict, folder_path: str, timestamp: str, config: dict):
    video_url = info.get('original_url')
    creator_url = info.get('uploader_url')
    
    # Retrieved will be the dict containing our scraped and parsed data
    retrieved = None
    
    # Scrape and parse data
    if video_url and creator_url:
        video_data = extract_data(video_url)
        creator_data = extract_data(creator_url)
        
        retrieved = parse_data(creator_data, video_data)
    
    # All the video-related metadata
    video = [
        f"Title: {info.get('title')}" if config.get('title') == True else None,
        f"Description: {info.get('description')}" if config.get('description') == True else None,
        f"Views: {info.get('view_count')}" if config.get('views') == True else None,
        f"Likes: {info.get('like_count')}" if config.get('likes') == True else None,
        f"Saves: {info.get('save_count')}" if config.get('saves') == True else None,
        f"Comments: {info.get('comment_count')}" if config.get('comments') == True else None,
        f"Reposts: {info.get('repost_count')}" if config.get('reposts') == True else None,
    ]
    
    # All the creator-related metadata
    user = [
        f"Username: {retrieved.get('username')}" if config.get('username') == True else None,
        f"Display Name: {retrieved.get('display_name')}" if config.get('display name') == True else None,
        f"Followers: {retrieved.get('followers')}" if config.get('followers') == True else None,
        f"Following: {retrieved.get('following')}" if config.get('following') == True else None,
        f"Bio: \n{retrieved.get('bio')}" if config.get('bio') == True else None,
    ]
    
    # All the sound-related metadata
    sound = [
        f"Sound Name: {info.get('track')}" if config.get('name') == True else None,
        f"Sound Creator: {info.get('artist')}" if config.get('creator') == True else None
    ]
    
    # Format the metadata txt file
    output = "\n\n".join([
        section("Video Information", [f"Video Url: {video_url}"], video if video else []), 
        section("Uploader Information", [f"Uploader Url: {creator_url}"], user if user else []),
        section("Sound Information", [f"Sound Url: {retrieved.get('sound_url')}",f"Raw Sound Url: {retrieved.get('raw_sound_url')}"], sound if sound else [])
        ])
    
    # Create the file named the current timestamp + _info
    with open(folder_path / f"{timestamp}_info.txt", 'w', encoding='utf-8') as f:
        f.write(output)