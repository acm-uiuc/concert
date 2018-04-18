import soundcloud
import pafy
import requests
import json
from config import config

sc_client = soundcloud.Client(client_id=config['SOUNDCLOUD_CLIENT_ID'])
yt_key = config['YT_API_KEY']

YT_BASE_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'

def parse_search_query(q, part, max_results):
    all_tracks = []
    # Check for user given urls
    if "youtube.com" in q:
        try:
            yt_playlist = pafy.get_playlist(q)
            playlist_item = parse_yt_playlist(yt_playlist, q)
            all_tracks.append(playlist_item)
        except Exception as e:
            pass
    elif "soundcloud.com" in q:
        try:
            sc_object = sc_client.get('/resolve', url=q)
            if sc_object.fields()["kind"] == "playlist":
                playlist = sc_client.get('/playlists/' + str(sc_object.id))
                first_song = playlist.tracks[0]
                sc_track = parse_sc_track(first_song, title=playlist.title, url=q)
                all_tracks.append(sc_track)
            else:
                track = sc_client.get('/tracks/' + str(sc_object.id)).fields()
                sc_track = parse_sc_track(track)
                all_tracks.append(sc_track)
        except requests.exceptions.HTTPError:
            logger.warning('Soundcloud track unavailable')

    if len(all_tracks) > 0:
        return json.dumps({"items": all_tracks})

    # Get General Search Results
    search_url  = YT_BASE_URL + "/?q=" + q + "&part=" + part + "&maxResults=" + max_results + "&key=" + yt_key
    resp = requests.get(search_url)
    yt_tracks = resp.json()["items"]
    for track in yt_tracks:
        try:
            vid = track["id"]["videoId"]
            yt_track = parse_yt_video(vid, track["snippet"])
            all_tracks.append(yt_track)
        except:
            pass

    tracks = sc_client.get('/tracks.json', q=q, limit=15)
    for track in tracks:
        sc_track = parse_sc_track(track.fields())
        all_tracks.append(sc_track)

    return json.dumps({"items": all_tracks})

def parse_sc_track(track, title=None, url=None):
    if track["artwork_url"] == None:
        track["artwork_url"] = ""
    if title == None:
        title = track["title"]
    if url == None:
        url = track["permalink_url"]
    sc_track = {
        "id": track["id"],
        "title": title,
        "thumbnail": track["artwork_url"],
        "url": url,
        "trackType": "SoundCloud"
    }
    return sc_track

def parse_yt_video(vid, snippet):
    url = "https://www.youtube.com/watch?v=" + vid
    yt_track = {
        "id": vid,
        "title": snippet["title"],
        "thumbnail": snippet["thumbnails"]["high"]["url"],
        "url": url,
        "trackType": "YouTube"
    }
    return yt_track

def parse_yt_playlist(yt_playlist, q):
    first_song = yt_playlist["items"][0]["pafy"]
    thumbnail_url = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, first_song.videoid, MQ_THUMBNAIL)
    playlist_object = {
        "id": yt_playlist["playlist_id"],
        "thumbnail": thumbnail_url,
        "title": yt_playlist["title"],
        "url": q,
        "trackType": "YouTubePlaylist"
    }
    return playlist_object