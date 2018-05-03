import requests
import json
import shutil
import os
from utils.youtube import search_yt_video, format_yt_playlist_result, get_yt_playlist
from utils.soundcloud import get_sc_object, get_sc_playlist, get_sc_track, search_sc_tracks, format_sc_search_result
from utils.spotify import format_sp_playlist_result, search_sp_tracks

MAX_RESULTS = 10
THUMBNAIL_PATH = os.path.join('static', 'thumbnails/')
JPG_EXTENSION = '.jpg'
DEFAULT_THUMBNAIL = "https://i.ytimg.com/vi/gh_dFH-Waes/maxresdefault.jpg"

def parse_search_query(q):
    """Returns search results based on user given query.

    Will first attempt to see if the query is a url representing a YouTube playlist,
    soundcloud playlist, soundcloud track, or Spotify track before doing a general search.

    Args:
        q (str): Search query

    Returns:
        JSON string containing list of results
    """
    all_tracks = []
    if "youtube.com" in q:
        try:
            yt_playlist = format_yt_playlist_result(get_yt_playlist(q), q)
            all_tracks.append(yt_playlist)
        except Exception as e:
            pass
    elif "soundcloud.com" in q:
        try:
            sc_object = get_sc_object(q)
            if sc_object.fields()["kind"] == "playlist":
                sc_playlist = get_sc_playlist(sc_object.id)
                first_song = sc_playlist[0]
                sc_playlist_result = format_sc_search_result(first_song, title=sc_object.title, url=q)
                all_tracks.append(sc_playlist_result)
            else:
                sc_track = get_sc_track(sc_object.id)
                sc_track_result = format_sc_search_result(sc_track)
                all_tracks.append(sc_track_result)
        except requests.exceptions.HTTPError:
            logger.warning('Soundcloud track unavailable')
    elif "spotify.com" in q:
        try:
            sp_playlist = format_sp_playlist_result(q)
            all_tracks.append(sp_playlist)
        except Exception as e:
            pass

    if len(all_tracks) > 0:
        return json.dumps({"items": all_tracks})

    # Get General Search Results
    yt_tracks = search_yt_video(q, MAX_RESULTS)
    all_tracks += yt_tracks

    sp_tracks = search_sp_tracks(q)
    all_tracks += sp_tracks

    sc_tracks = search_sc_tracks(q)
    all_tracks += sc_tracks

    return json.dumps({"items": all_tracks})


def download_thumbnail(primary_url, secondary_url, song_id):
    """Helper function that downloads thumbnails for songs

    Args:
        primary_url (str): The first thumbnail url to try to download
        secondary_url (str): The backup thumbnail url to try to download
        song_id (str): The id of the song whose thumbnail is being downloaded

    Returns:
        str: The path of the image that was download. Empty string if both urls failed
    """
    path = "{}{}{}".format(THUMBNAIL_PATH, song_id, JPG_EXTENSION)
    if os.path.isfile(path):
        return path

    r1 = requests.get(primary_url, stream=True)
    if r1.status_code == 200:
        with open(path, 'wb+') as f:
            r1.raw.decode_content = True
            shutil.copyfileobj(r1.raw, f)  
        return path

    r2 = requests.get(secondary_url, stream=True)
    if r2.status_code == 200:
        with open(path, 'wb+') as f:
            r2.raw.decode_content = True
            shutil.copyfileobj(r2.raw, f)  
        return path

    return ""  