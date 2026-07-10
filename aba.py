import requests, json, re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/148.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def extract_data(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=20)
    
    response.raise_for_status()
    
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        response.text, re.DOTALL)
    if not match:
        return None
    
    return match.group(1)

with open("json.txt", "w", encoding="utf-8") as file:
    url = "https://www.tiktok.com/@cat7cc"
    
    data = str(extract_data(url))
    
    if not data:
        print("fuck")
    if data:
        file.write(data)
        print(data)
        print(file)