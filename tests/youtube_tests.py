import unittest
from utils.youtube import *

class YouTubeUtilsTest(unittest.TestCase):
	
	def test_search_yt_video(self):
		'''
		Make sure we can search for videos from YouTube
		'''
		q = "Drake - God's Plan"
		results = search_yt_video(q)
		top_result = results[0]
		self.assertEqual(top_result['id'], 'xpVfcZ0ZcFM')
		self.assertEqual(top_result['title'], 'Drake - God\'s Plan')
		self.assertEqual(top_result['url'], 'https://www.youtube.com/watch?v=xpVfcZ0ZcFM')
		self.assertEqual(top_result['trackType'], 'YouTube')

	def test_get_yt_video(self):
		'''
		Make sure pafy is retrieving the right track
		'''
		url = "https://www.youtube.com/watch?v=Kp7eSUU9oy8"
		video = get_yt_video(url)
		self.assertEqual(video.title, "Childish Gambino - Redbone (Official Audio)")
		self.assertEqual(video.videoid, "Kp7eSUU9oy8")

	def test_get_yt_playlist(self):
		'''
		Test to see if pafy is retrieving playlists
		'''
		url = "https://www.youtube.com/watch?v=si81bIoZRJQ&list=PLcW3obwtpNMhXyT88enp-6ZST2O8WFA0r"
		playlist = get_yt_playlist(url)
		assert playlist is not None

	def test_get_yt_audio(self):
		'''
		Test to see if pafy is retrieving the correct YouTube audio for a given song
		'''
		sp_track = {
			"name": "RedBone",
			"artists": ["Childish Gambino"]
		}
		video = get_yt_audio(sp_track)
		self.assertEqual(video.title, "Childish Gambino - Redbone (Official Audio)")
		self.assertEqual(video.videoid, "Kp7eSUU9oy8")


if __name__ == '__main__':
    unittest.main()