from models import Song
import vlc
import time


class Player:
	def __init__(self):
		self.instance = vlc.Instance('--no-video')
		self.player = self.instance.media_player_new()
		self.volume = 70
		self.player.audio_set_volume(self.volume)
		self.current_track = None


	def set_volume(self, value):
		#Mox volume is 100
		if value > 100:
			value = 100

		self.volume = value
		self.player.audio_set_volume(value)
		return self.get_state()


	def play(self, mrl):
		m = self.instance.media_new(mrl)
		self.player.set_media(m)
		self.player.play()
		return self.get_state()


	def pause(self):
		self.player.pause()
		return self.get_state()


	def stop(self):
		self.player.stop()
		self.current_track = None
		return self.get_state()


	def get_state(self):
		media = self.player.get_media()
		audio_status = self.player.get_state()
		state = {'audio_status': audio_status, 'volume': self.volume}

		if media:
			state['media'] = vlc.bytes_to_str(media.get_mrl())
			state['current_time'] = self.player.get_time()
			state['duration'] = media.get_duration()

		return state
