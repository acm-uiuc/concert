class Song:
	#Will add more parameters later
	def __init__(self, mrl, title, url):
		self.mrl = mrl
		self.title = title
		self.url = url

	def dictify(self):
		return {
			'url': self.url,
			'mrl': self.mrl,
			'title': self.title
		}