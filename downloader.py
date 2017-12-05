import youtube_dl
from models import Song
from pymongo import MongoClient

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'music/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    "extractaudio": True,
    "noplaylist": False
}
ytdl = youtube_dl.YoutubeDL(ydl_opts)

client = MongoClient()
db = client.concert

#Downloads a song
def download_song(url):
	info = ytdl.extract_info(url, download=True)
    
	song_id = info["id"]
	song_title = info["title"]

	#This is jank for now
	song_mrl = "music/" + str(song_id) + ".mp3"

	new_song = Song(song_mrl, song_title)
	db.Queue.insert_one(new_song.dictify())