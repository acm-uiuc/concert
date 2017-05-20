import youtube_dl

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'tmp/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
}
ytdl = youtube_dl.YoutubeDL(ydl_opts)

#Downloads a song
def download_song(url):
	ytdl.download([url])
