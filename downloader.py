import yt_dlp

def download_video(urls: list, path: str):
    options = {
        'format': 'best',
        'outtmpl': f'{path}/%(title)s.%(ext)s',
    }
    
    for url in (urls):
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download(url)
        
path = "C:/Users/neina/Desktop/Videos"
download_video(['https://www.tiktok.com/@cat7cc/video/7619782378092776712'], path)