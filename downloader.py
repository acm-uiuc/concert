import youtube_dl

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'tmp/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class Downloader:
	def __init__(self, destination=None):
		self.destination = destination
		self.ytdl = youtube_dl.YoutubeDL(ydl_opts)

	def downloader(self):
		return self.ytdl

	def download_song(self, url):
		return self.ytdl.download([url])