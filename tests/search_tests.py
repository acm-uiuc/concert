import json
import unittest
from utils.searchutils import *

class SearchUtilsTest(unittest.TestCase):
	
	def test_search_basic(self):
		"""
		Basic search test to make sure concert is retrieving tracks from
		YouTube, SoundCloud, and Spotify
		"""
		q = 'Drake'
		results = json.loads(parse_search_query(q))["items"]
		track_types = set()
		for result in results:
			track_types.add(result["trackType"])
		self.assertEqual(len(track_types), 3)

	def test_search_hard(self):
		"""
		Test to see if search is only returning a single link
		representing the video below (Casey Neistat - Why I Wear a Suit??)
		"""
		q = 'https://www.youtube.com/watch?v=66DMQMSUvII'
		results = json.loads(parse_search_query(q))["items"]
		first_result = results[0]
		self.assertEqual(len(results), 1)
		self.assertEqual(first_result["trackType"], "YouTube")

	def test_search_yt_playlist(self):
		"""
		Test to see if search is returning a single result representing
		a playlist on YouTube (Porter Robinson - Worlds full album)
		"""
		q = 'https://www.youtube.com/watch?v=si81bIoZRJQ&list=PLcW3obwtpNMhXyT88enp-6ZST2O8WFA0r'
		results = json.loads(parse_search_query(q))["items"]
		first_result = results[0]
		self.assertEqual(len(results), 1)
		self.assertEqual(first_result["title"], "Porter Robinson - Worlds full album")
		self.assertEqual(first_result["trackType"], "YouTubePlaylist")

	def test_search_sc_playlist(self):
		"""
		Test to see if search returns a single result representing 
		a playlist on Soundcloud (Test)
		"""
		q = 'https://soundcloud.com/tommy-yu-3/sets/test'
		results = json.loads(parse_search_query(q))["items"]
		first_result = results[0]
		self.assertEqual(len(results), 1)
		self.assertEqual(first_result["title"], "Test")
		self.assertEqual(first_result["trackType"], "SoundCloud")

	def test_search_sc_track(self):
		"""
		Test to see if search returns a single result representing
		a track on Soundcloud (marshmello - Alone)
		"""
		q = 'https://soundcloud.com/marshmellomusic/alone'
		results = json.loads(parse_search_query(q))["items"]
		first_result = results[0]
		self.assertEqual(len(results), 1)
		self.assertEqual(first_result["title"], "Alone (Original Mix)")
		self.assertEqual(first_result["trackType"], "SoundCloud")

	def test_search_spotify_playlist(self):
		"""
		Test to see if search returns a single result representing
		a playlist on Spotify (Concert - Test)
		"""
		q = 'https://open.spotify.com/user/1230457405/playlist/6mes1NJg3vzvpr4VefrcWu?si=zj5OTDnNS52p2AlSes2PYg'
		results = json.loads(parse_search_query(q))["items"]
		first_result = results[0]
		self.assertEqual(len(results), 1)
		self.assertEqual(first_result["title"], "Concert - Test")
		self.assertEqual(first_result["trackType"], "SpotifyPlaylist")

if __name__ == '__main__':
    unittest.main()