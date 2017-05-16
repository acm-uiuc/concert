from models import Song
from player import Player
from downloader import Downloader
import vlc
import time
import threading

class MusicService:
	def __init__(self):
		self.player = Player()
		self.dl = Downloader()
		self.queue = []
		new_song = Song("tmp/test.mp3", "Title", "Artist")
		self.queue.append(new_song)

	#Implement this with downloader later
	def add_song(self, url):
		new_song = get_song(url)
		queue.append(new_song)
		return

	def play_next(self):
		if len(self.queue) > 0:
			next_song = self.queue.pop(0)
			self.player.play(next_song.mrl)

	def player_thread(self):
		while True:
			cur_state = self.player.get_state()["audio_status"]
			if cur_state in [vlc.State.Ended, vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Error]:
				self.play_next()
			time.sleep(.30)

	def start(self):
		thread = threading.Thread(target=self.player_thread)
		thread.daemon = True
		thread.start()