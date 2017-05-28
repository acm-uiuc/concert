class Song:
	#Will add more parameters later
	def __init__(self, mrl, title):
		self.mrl = mrl
		self.title = title

	def dictify(self):
		return {
			'mrl': self.mrl,
			'title': self.title
		}