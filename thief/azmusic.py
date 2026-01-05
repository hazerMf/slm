import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin

def save_lyrics(album, song, content):
    # Path: slm/food/Album/Song.txt
    folder_path = os.path.join("food", album.strip().replace("/", "-"))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    file_path = os.path.join(folder_path, f"{song.strip().replace('/', '-')}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully saved: {song} in {album}")

def scrape_song_page(url):
    headers = {"User-Agent": "batman bin suparman"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 1. IDENTIFY ALBUM AND SONG NAME
    # Note: You'll need to inspect the page to get the exact tags for these
    #try:
    song = soup.find("div",class_="ringtone").find_next_sibling("b").text.replace('"', '') 
    song_name = re.sub(r'[\\/:*?"<>|\']', '', song).replace(' ', '_')
    album = soup.find("div", class_="songinalbum_title").find('b').text.replace('"', '').strip()
    album_name = re.sub(r'[\\/:*?"<>|\']', '', album).replace(' ', '_')
    #except:
    #    song_name = "Unknown_Song"
    #    album_name = "Unknown_Album"

    # 2. EXTRACT LYRICS (Using the Comment Anchor)
    comment = soup.find(string=lambda t: isinstance(t, Comment) and "licensing agreement" in t)
    lyrics = []
    if comment:
        for sibling in comment.next_siblings:
            if sibling.name == '/div': break
            if isinstance(sibling, str): lyrics.append(sibling.strip())
            elif sibling.name == 'br': lyrics.append('\n')
    
    lyrics_text = "".join(lyrics).strip()
    
    # Save the data
    global cnt

    save_lyrics(album_name, f"{cnt}.{song_name}", lyrics_text)

    
    cnt += 1

    # 3. FIND NEXT SONG LINK
    next_song_link = None

    # Locate the album panel containing all songs
    album_panel = soup.find("div", class_="songlist-panel")

    if album_panel:
        # Find all song links within this specific panel
        # The 'a' tags are inside divs with class 'listalbum-item'
        all_links = album_panel.find_all("a")
        
        for i, link in enumerate(all_links):
            # Check if this link matches the page we are currently on
            # We use 'in' because the href might be relative
            if link['href'] in url:
                # If there is a next link in the list, grab it
                if i + 1 < len(all_links):
                    next_tag = all_links[i + 1]
                    next_song_link = urljoin(url, next_tag['href'])
                    break 
                else:
                    # We are at the last song of the album
                    print("Reached the end of the album list.")
                    next_song_link = None

    delay = random.uniform(3, 6)
    time.sleep(delay)

    return next_song_link

# --- MAIN EXECUTION ---
start_urls = [
    "https://www.azlyrics.com/lyrics/mfdoom/thetimewefaceddoomskit.html",
    "https://www.azlyrics.com/lyrics/mfdoom/theillestvillains.html",
    "https://www.azlyrics.com/lyrics/mfdoom/beefrapp.html",
    "https://www.azlyrics.com/lyrics/deftones/myownsummershoveit.html",
    "https://www.azlyrics.com/lyrics/tylerthecreator/igorstheme.html",
    "https://www.azlyrics.com/lyrics/deftones/changeinthehouseofflies.html",
    "https://www.azlyrics.com/lyrics/linkinpark/papercut.html",
    "https://www.azlyrics.com/lyrics/limpbizkit/introchocolatestarfishandthehotdogflavoredwater.html",
    "https://www.azlyrics.com/lyrics/kendricklamar/wesleystheory.html",

]

for start_url in start_urls:
    current_url = start_url
    cnt = 1
    
    # This loop follows the "Next" links until the album ends
    while current_url:
        print(f"Processing: {current_url}")
        next_url = scrape_song_page(current_url)
        
        # Move to next song
        current_url = next_url
        
        # Delay
        delay = random.uniform(3, 6)
        time.sleep(delay)