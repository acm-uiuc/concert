import youtube_dl
from models import Song

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'music/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
}
ytdl = youtube_dl.YoutubeDL(ydl_opts)

#Downloads a song
def download_song(url):
	info = ytdl.extract_info(url, download=True)
	song_id = info["id"]
	song_title = info["title"]

	#This is jank for now
	song_mrl = "music/" + str(song_id) + ".mp3"
	new_song = Song(song_id, song_mrl, song_title)
