from models import Song
import vlc
import time
import json

class Player:
	def __init__(self):
		self.instance = vlc.Instance('--no-video')
		self.vlc_player = self.instance.media_player_new()
		self.volume = 70
		self.vlc_player.audio_set_volume(self.volume)
		self.current_track = None


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
		print("------PLAYING------")
		print("mrl: %s" % mrl)
		print("is_playing (called from play): %r" % self.is_playing())
		print("------PLAYING------")
		#print("status: %d" % status)
		return self.cur_state()


	def pause(self):
		self.vlc_player.pause()
		time.sleep(0.1)
		return self.cur_state()


	def stop(self):
		self.vlc_player.stop()
		self.current_track = None
		return self.cur_state()


	def is_playing(self):
		audio_status = self.vlc_player.get_state()
		if audio_status in {vlc.State.Ended, vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Error}:
			#self.vlc_player.set_media(None)
			return False
		return True

	def set_time(self, percent):
		duration = self.cur_state()['duration']
		self.vlc_player.set_time(int(duration * percent))
		

	def cur_state(self):
		media = self.vlc_player.get_media()
		audio_status = self.vlc_player.get_state()

		state = {'audio_status': str(audio_status), 'volume': self.volume, 'is_playing': self.is_playing()}

		if media:
			state['media'] = vlc.bytes_to_str(media.get_mrl())
			state['current_time'] = self.vlc_player.get_time()
			state['duration'] = media.get_duration()
			if self.current_track != None:
				state['current_track'] = self.current_track['title']
			else:
				state['current_track'] = 'None'
		else:
			state['media'] = None
		
		json_str = json.dumps(state)
		return json_str
