import vlc
import time
import json
import urllib
from models import Song
from pathlib import Path

DEFAULT_VOLUME = 70
MAX_VOLUME = 100
MAX_NETWORK_PINGS = 5
NETWORK_ATTEMPT_DELAY = 1
MAX_PLAY_ATTEMPTS = 5
PLAY_ATTEMPT_DELAY = 0.3
PAUSE_DELAY = 0.1

class Player:
    def __init__(self):
        self.instance = vlc.Instance('--no-video')
        self.vlc_player = self.instance.media_player_new()
        self.volume = DEFAULT_VOLUME
        self.vlc_player.audio_set_volume(self.volume)
        self.current_track = None

    def set_volume(self, value):
        value = min(value, MAX_VOLUME)
        self.volume = value
        self.vlc_player.audio_set_volume(value)
        payload = {
            'volume': self.volume
        }
        return json.dumps(payload)

    def play(self, song):
        self.vlc_player.stop()
        mrl = song['mrl']
        m = self.instance.media_new(mrl)

        network_attempts = 0
        while not self._network_available(mrl):
            network_attempts += 1
            if network_attempts == MAX_NETWORK_PINGS:
                return self.cur_state()

        play_attempts = 0
        while not self.is_playing():
            if play_attempts == MAX_PLAY_ATTEMPTS:
                return self.cur_state()
            self.vlc_player.stop()
            self.vlc_player.set_media(m)
            self.vlc_player.play()
            self.current_track = song
            play_attempts += 1
            time.sleep(PLAY_ATTEMPT_DELAY)

        print("------PLAYING------")
        print("Title: %s" % song['title'])
        print("mrl: %s" % mrl)
        print("is_playing (called from play): %r" % self.is_playing())
        print("------PLAYING------")

        return self.cur_state()

    def pause(self):
        self.vlc_player.pause()
        # We need this so the vlc library can update
        time.sleep(PAUSE_DELAY) 
        media = self.vlc_player.get_media()
        payload = {'audio_status': str(self.vlc_player.get_state()), 'is_playing': self.is_playing()}
        if media:
            payload['current_time'] = self.vlc_player.get_time()
            payload['duration'] = self.current_track['duration']
        return json.dumps(payload)

    def stop(self):
        if self.current_track != None:
            self.vlc_player.stop()
            self.current_track = None
        return self.cur_state()

    def is_playing(self):
        audio_status = self.vlc_player.get_state()
        if audio_status in {vlc.State.Ended, vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Error}:
            self.vlc_player.set_media(None)
            self.current_track = None
            return False
        return True

    def set_time(self, percent):
        duration = self.cur_state()['duration']
        self.vlc_player.set_time(int(duration * percent))
        return self.cur_state()

    def cur_state(self):
        media = self.vlc_player.get_media()
        audio_status = self.vlc_player.get_state()
        state = {'audio_status': str(audio_status), 'volume': self.volume, 'is_playing': self.is_playing()}

        if media:
            state['media'] = vlc.bytes_to_str(media.get_mrl())
            state['current_time'] = self.vlc_player.get_time()
            if self.current_track != None:
                state['current_track'] = self.current_track['title']
                state['duration'] = self.current_track['duration']
                state['thumbnail'] = self.current_track['thumbnail']
            else:
                state['current_track'] = None
                state['duration'] = -1
                state['thumbnail'] = ''
        else:
            state['media'] = None

        return json.dumps(state)

    def _file_exists(self, mrl):
        file = Path(mrl)
        return file.is_file()

    def _network_available(self, url):
        try:
            urllib.request.urlopen(url, timeout=NETWORK_ATTEMPT_DELAY)
            print("Pinged: "+ url)
            return True
        except urllib.error.URLError as err:
            return False
