from flask_login import UserMixin
from utils.searchutils import download_thumbnail

YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'

class Song:
    def __init__(self, id="", stream="", title="", duration="", thumbnail="", playedby=""):
        self.id = id
        self.stream = stream
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.playedby = playedby

    def from_yt_video(yt_video, playedby):
        s = Song()
        # Get video information
        s.title = yt_video.title
        s.id = str(yt_video.videoid)
        s.duration = yt_video.length * 1000
        s.stream = yt_video.audiostreams[0].url
        s.playedby = playedby

        thumbnail_1 = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, s.id, MAXRES_THUMBNAIL)
        thumbnail_2 = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, s.id, MQ_THUMBNAIL)
        s.thumbnail = download_thumbnail(thumbnail_1, thumbnail_2, s.id)
        return s

    def from_sc_track(sc_track, playedby):
        s = Song()
        # Get song information
        s.title = sc_track["title"]
        s.id = str(sc_track["id"])
        s.duration = sc_track["duration"]
        s.stream = sc_track["stream"]
        s.playedby = playedby

        try:
            thumbnail_1 = sc_track["artwork_url"].replace('large', 't500x500')
            thumbnail_2 = sc_track["artwork_url"].replace('large', 'crop')
        except:
            thumbnail_1 = DEFAULT_THUMBNAIL
            thumbnail_2 = DEFAULT_THUMBNAIL
        s.thumbnail = download_thumbnail(thumbnail_1, thumbnail_2, s.id)
        return s
    
    def from_sp_track(sp_track, yt_video, playedby):
        s = Song()
        # Merge Spotify Metadata with Youtube Stream
        s.title = sp_track["name"] + " - " + ', '.join(sp_track["artists"])
        s.id = str(yt_video.videoid)
        s.duration = yt_video.length * 1000
        s.stream = yt_video.audiostreams[0].url
        s.playedby = playedby

        thumbnail_1 = sp_track["art"]
        thumbnail_2 = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, s.id, MAXRES_THUMBNAIL)
        s.thumbnail = download_thumbnail(thumbnail_1, thumbnail_2, s.id)
        return s

    def dictify(self):
        return {
            'id': self.id,
            'stream': self.stream,
            'title': self.title,
            'duration': self.duration,
            'thumbnail': self.thumbnail,
            'playedby': self.playedby
        }


class User(UserMixin):
    def __init__(self, uid, first_name, last_name):
        self.uid = str(uid)
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return self.uid

    def get_by_id(db, uid):
        return db.Users.find_one({'uid': uid})
