import requests
import pafy
from config import config

# YouTube API Key
yt_key = config['YT_API_KEY']

YT_BASE_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'
MAX_RESULTS = 10

def search_yt_video(q, limit=MAX_RESULTS):
	"""Searches YouTube for videos based on user query

	Args:
		q (str): Query to search for
		limit (int, optional): Limit of the number of results to return
	Returns:
		List of formatted, valid YouTube tracks 
	"""
	search_url  = YT_BASE_URL + "/?q=" + q + "&part=snippet&maxResults=" + str(limit) + "&key=" + yt_key
	resp = requests.get(search_url)
	tracks = resp.json()["items"]
	yt_tracks = []
	for track in tracks:
		try:
			vid = track["id"]["videoId"]
			yt_track = format_yt_search_result(vid, track["snippet"])
			yt_tracks.append(yt_track)
		except:
			pass
	return yt_tracks

def get_yt_video(url):
	"""Retrieves YouTube video object of given url using Pafy

	Args:
		url (str): Url of the YouTube video
	Returns:
		Pafy YouTube object
	"""
	return pafy.new(url)

def format_yt_search_result(vid, snippet):
	"""Formats a YouTube search result to be displayed to clients

	Args:
		vid (str): Id of the video
		snippet (dict): Dict that is returned from the YouTube search API
	Returns:
		Dict of the formatted snippet, extracting only neccessary info from it
	"""
	url = "https://www.youtube.com/watch?v=" + vid
	yt_track = {
		"id": vid,
		"title": snippet["title"],
		"thumbnail": snippet["thumbnails"]["high"]["url"],
		"url": url,
		"trackType": "YouTube"
	}
	return yt_track

def get_yt_playlist(url):
	"""Retrieves YouTube playlist object from Pafy

	Args:
		url (str): Url of the playlist
	Returns:
		Formatted pafy playlist object
	"""
	return format_yt_playlist_result(pafy.get_playlist(url), url)

def format_yt_playlist_result(yt_playlist, url):
	"""Formats a pafy playlist object to be displayed to clients

	Args:
		yt_playlist (dict): Pafy playlist object
	Returns:
		Dict containing neccessary info for clients
	"""
	first_song = yt_playlist["items"][0]["pafy"]
	thumbnail_url = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, first_song.videoid, MQ_THUMBNAIL)
	playlist_object = {
		"id": yt_playlist["playlist_id"],
		"thumbnail": thumbnail_url,
		"title": yt_playlist["title"],
		"url": url,
		"trackType": "YouTubePlaylist"
	}
	return playlist_object

def get_yt_audio(sp_track):
	"""Retrieves the YouTube video that matches best to a given spotify track

	Args:
		sp_track (dict): Spotify track dictionary
	Returns:
		Pafy video object of the best YouTube match to the spotify track
	"""
	query = sp_track["name"] + " - " + " ,".join(sp_track["artists"])
	yt_track = search_yt_video(query, 1)[0]
	video_url = "https://www.youtube.com/watch?v=" + yt_track["id"]
	return get_yt_video(video_url)