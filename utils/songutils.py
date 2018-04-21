import soundcloud
import spotipy
import pafy
import requests
import json
from config import config
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse

YT_BASE_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'
MAX_RESULTS = 10

# Setup Soundcloud API
sc_client = soundcloud.Client(client_id=config['SOUNDCLOUD_CLIENT_ID'])
yt_key = config['YT_API_KEY']

# Setup Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=config["SPOTIFY_CLIENT_ID"],
    client_secret=config["SPOTIFY_CLIENT_SECRET"])
sp_client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def parse_search_query(q):
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
    elif "spotify.com" in q:
        try:
            spotify_playlist = parse_spotify_playlist(q)
            all_tracks.append(spotify_playlist)
        except Exception as e:
            pass

    if len(all_tracks) > 0:
        return json.dumps({"items": all_tracks})

    # Get General Search Results
    yt_tracks = yt_search(q, MAX_RESULTS)
    for track in yt_tracks:
        try:
            vid = track["id"]["videoId"]
            yt_track = parse_yt_video(vid, track["snippet"])
            all_tracks.append(yt_track)
        except:
            pass

    sp_tracks = sp_client.search(q=q, type='track', limit=5)["tracks"]["items"]
    for track in sp_tracks:
        sp_track = parse_sp_track(track)
        all_tracks.append(sp_track)

    sc_tracks = sc_client.get('/tracks.json', q=q, limit=MAX_RESULTS)
    for track in sc_tracks:
        sc_track = parse_sc_track(track.fields())
        all_tracks.append(sc_track)

    return json.dumps({"items": all_tracks})

def yt_search(q, max_results=MAX_RESULTS):
    search_url  = YT_BASE_URL + "/?q=" + q + "&part=snippet&maxResults=" + str(max_results) + "&key=" + yt_key
    resp = requests.get(search_url)
    yt_tracks = resp.json()["items"]
    return yt_tracks

def get_spotify_track(track_id):
    return sp_client.track(track_id)

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

def parse_sp_track(track):
    artists = [artist["name"] for artist in track["artists"]]
    title = track["name"] + " - " + ', '.join(artists)
    if len(track["album"]["images"]) > 0:
        thumbnail = track["album"]["images"][0]["url"]
    else:
        thumbnail = ""
    sp_track = {
        "id": track["id"],
        "title": title,
        "thumbnail": thumbnail,
        "url": track["uri"],
        "trackType": "Spotify"
    }
    return sp_track

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

def get_spotify_playlist(url, fields, only_tracks=False):
    o = urlparse(url)
    path = o.path
    username = path.split('/')[2]
    playlist_id = path.split('/')[4]
    if not only_tracks:
        return sp_client.user_playlist(username, playlist_id, fields=fields)
    else:
        return sp_client.user_playlist_tracks(username, playlist_id, fields=fields)

def parse_spotify_playlist(url):
    playlist = get_spotify_playlist(url, "images,name,id")
    playlist_object = {
        "id": playlist["id"],
        "thumbnail": playlist["images"][0]["url"],
        "title": playlist["name"],
        "url": url,
        "trackType": "SpotifyPlaylist"
    }
    return playlist_object