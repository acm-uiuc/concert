from concert.thridparty import vlc
import time
import urllib
from concert.models import Song
from pathlib import Path

class ConcertPlayer:
    def __init__(self, config):
        self.instance = vlc.Instance('--no-video')
        self.vlc_player = self.instance.media_player_new()
        self.volume = 70
        self.vlc_player.audio_set_volume(self.volume)
        self.current_track = None

        self.NETWORK_TIMEOUT = config["network_timeout"]
        self.VLC_TIMEOUT = self.NETWORK_TIMEOUT

    def player_state(self):
        media = self.vlc_player.get_media()
        audio_status = self.vlc_player.get_state()
        state = {
                'audio_status': str(audio_status), 
                'volume': self.volume, 
                'is_playing': self.is_playing(),
                'current_track_info': None
        }

        if media and self.current_track != None:
            state["current_track_info"] = {
                'title': self.current_track['title'],
                'duration': self.current_track['duration'],
                'thumbnail_url': self.current_track['thumbnail_url'],
                'current_time': self.vlc_player.get_time(),
                'playedby': self.current_track["playedby"]
            }
        return state


    def play(self, song):
        self.vlc_player.stop()
        mrl = song['track_url']
        m = self.instance.media_new(mrl)

        count = 0
        while not self.network_available(mrl):
            count += 1
            if count == self.NETWORK_TIMEOUT:
                return 

        count = 0
        while not self.is_playing():
            if count == self.VLC_TIMEOUT:
                return 
            self.vlc_player.stop()
            self.vlc_player.set_media(m)
            self.vlc_player.play()
            self.current_track = song
            count += 1
            time.sleep(0.3)

        print("------PLAYING------")
        print("Title: %s" % song['title'])
        print("Track URL is: %s" % mrl)
        print("is_playing (called from play): %r" % self.is_playing())
        print("------PLAYING------")

    def pause(self):
        self.vlc_player.pause()
        time.sleep(0.1) #We need this so the vlc library can update

    def stop(self):
        if (self.current_track != None):
            self.vlc_player.stop()
            self.current_track = None

    def set_time(self, percent):
        duration = self.player_state()['duration']
        self.vlc_player.set_time(int(duration * percent))

    def set_volume(self, value):
        # Max volume is 100
        if value > 100:
            value = 100
        self.volume = value
        self.vlc_player.audio_set_volume(value)


    def is_playing(self):
        audio_status = self.vlc_player.get_state()
        if audio_status in {vlc.State.Ended, vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Error}:
            self.vlc_player.set_media(None)
            self.current_track = None
            return False
        return True

    def network_available(self, url):
        try:
            urllib.request.urlopen(url, timeout=1)
            print("Pinged: "+ url)
            return True
        except urllib.error.URLError:
            return False
