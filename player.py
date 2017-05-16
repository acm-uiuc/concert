from models import Song
import vlc
import time


class Player:
	def __init__(self):
		self.instance = vlc.Instance('--no-video')
		self.vlc_player = self.instance.media_player_new()
		self.volume = 70
		self.vlc_player.audio_set_volume(self.volume)


	def set_volume(self, value):
		#Max volume is 100
		if value > 100:
			value = 100

		self.volume = value
		self.vlc_player.audio_set_volume(value)
		return self.cur_state()


	def play(self, mrl):
		m = self.instance.media_new(mrl)
		self.vlc_player.set_media(m)
		self.vlc_player.play()
		return self.cur_state()


	def pause(self):
		self.vlc_player.pause()
		return self.cur_state()


	def stop(self):
		self.vlc_player.stop()
		return self.cur_state()


	def is_playing(self):
		audio_status = self.vlc_player.get_state()
		if audio_status in {vlc.State.Ended, vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Error}:
			print("STOPPED")
			return False
		return True


	def cur_state(self):
		media = self.vlc_player.get_media()
		audio_status = self.vlc_player.get_state()
		state = {'audio_status': audio_status, 'volume': self.volume}

		if media:
			state['media'] = vlc.bytes_to_str(media.get_mrl())
			state['current_time'] = self.vlc_player.get_time()
			state['duration'] = media.get_duration()

		return state
