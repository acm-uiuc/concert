from flask_login import UserMixin
from utils.searchutils import download_thumbnail

YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'

class Song:
    """The Song class encapsulates song data so it can be used by VLC and clients

    Args/Params:
        id (str): id of the song
        stream (str): url of the stream of the song
        title (str): title of the song
        duration (int): duration in milliseconds of the song
        thumbnail (str): the local path to the thumbnail of the song
        playedby (str): the name of the person who added the song
    """
    def __init__(self, id="", stream="", title="", duration=0, thumbnail="", playedby=""):
        self.id = id
        self.stream = stream
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.playedby = playedby

    def from_yt_video(yt_video, playedby):
        """Converts a yt_video to a Song instance

        Args:
            yt_video (Pafy video object): Video to transform
            playedby (str): Who played the song
        Returns:
            Song object containing the youtube video info
        """
        s = Song()
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
        """Converts a sc_track to a Song instance

        Args:
            sc_track (Soundcloud track object): Track to transform
            playedby (str): Who played the song
        Returns:
            Song object containing the soundcloud track info
        """
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
        """Converts a sp_track to a Song instance

        Uses Spotify's meta data to find the best matching YouTube audio stream

        Args:
            sp_track (Soundcloud track object): Track to transform
            playedby (str): Who played the song
        Returns:
            Song object containing the spotify track metadata with the youtube stream info
        """
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
        """Returns a dictionary version of the Song object"""
        return {
            'id': self.id,
            'stream': self.stream,
            'title': self.title,
            'duration': self.duration,
            'thumbnail': self.thumbnail,
            'playedby': self.playedby
        }


class User(UserMixin):
    """User class used for Flask_login"""
    def __init__(self, uid, first_name, last_name):
        self.uid = str(uid)
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return self.uid

    def get_by_id(db, uid):
        return db.Users.find_one({'uid': uid})
