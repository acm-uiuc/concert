import soundcloud
from concert.service.fetchers import Fetcher

class SoundcloudFetcher(Fetcher):
    def __init__(self, config):
        super().__init__(self)
        self.client_id = config["api_key"]
        self.sndcld = soundcloud.Client(client_id=config["api_key"])

    def fetch_song(self, url):
        if "soundcloud.com" not in url:
            raise ValueError("URL is not a Soundcloud URL")
        
        track_list = []
        try:
            resource = self.sndcld.get("/resolve", url=url).fields()
			##print(resource["kind"])
            if resource["kind"] == "playlist":
                for t in resource["tracks"]:
                    track_list.append(self.process_track_info(t))
            elif resource["kind"] == "track":
                track_list.append(self.process_track_info(resource))
        except Exception:
            pass #LOG EXCEPTION

        return track_list

    def process_track_info(self, track):
	    return {
            "track_url": track["stream_url"] + "?client_id=" + self.client_id,
            "title": track["title"],
            "duration": track["duration"],
            "thumbnail_url": track["artwork_url"].replace("large","t500x500")
        }
