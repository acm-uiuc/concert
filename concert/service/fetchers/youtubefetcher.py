import pafy
from concert.service.fetchers import Fetcher

class YoutubeFetcher(Fetcher):
    YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
    MAXRES_THUMBNAIL = '/maxresdefault.jpg'
    def __init__(self, config):
        super().__init__(self)

    def fetch_song(self, url):
        if "youtube.com" not in url:
            raise ValueError("URL is not a Youtube URL")

        tracks = []
        try:
            playlist = pafy.get_playlist(url)
            print(playlist)
            videos = playlist["items"]
            for video in videos:
                try:
                	tracks.append(self.process_track_info(video["pafy"]))
                except Exception:
                    pass

        except Exception:
            video = pafy.new(url)
            print(video)
            tracks.append(self.process_track_info(video))

        print(tracks)

        return tracks

    def process_track_info(self,track):
	    return {
            "track_url": track.audiostreams[0].url,
            "title": track.title,
            "duration": track.length * 1000,
            "thumbnail_url": "{}{}{}".format(self.YOUTUBE_THUMBNAIL_URL, track.videoid, self.MAXRES_THUMBNAIL)
        }
