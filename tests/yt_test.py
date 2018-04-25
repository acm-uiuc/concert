import unittest
from utils.youtube import *

class YouTubeUtilsTest(unittest.TestCase):
	
	def test_search_yt_video(self):
		q = "Drake - God's Plan"
		results = search_yt_video(q)
		top_result = results[0]
		self.assertEqual(top_result['id'], 'xpVfcZ0ZcFM')
		self.assertEqual(top_result['title'], 'Drake - God\'s Plan')
		self.assertEqual(top_result['url'], 'https://www.youtube.com/watch?v=xpVfcZ0ZcFM')
		self.assertEqual(top_result['trackType'], 'YouTube')

if __name__ == '__main__':
    unittest.main()