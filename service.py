from models import Song
from player import Player
import downloader as dl
import vlc
import time
import threading

class MusicService:
	def __init__(self):
		self.player = Player()
		self.queue = []
		new_song = Song("tmp/test.mp3", "Title", "Artist")
		self.queue.append(new_song)
		self.current_track = new_song

	#Implement this with downloader later
	def add_song(self, url):
		new_song = get_song(url)
		queue.append(new_song)
		return

	def play_next(self):
		if len(self.queue) > 0:
			next_song = self.queue.pop(0)
			self.player.play(next_song.mrl)
			self.current_track = next_song

	def player_thread(self):
		while True:
			if not self.player.is_playing():
				self.play_next()
			time.sleep(.30)

	def start(self):
		thread = threading.Thread(target=self.player_thread)
		thread.daemon = True
		thread.start()