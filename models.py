class Song:
	#Will add more parameters later
	def __init__(self, id, mrl, title):
		self.id = id
		self.mrl = mrl
		self.title = title

	def dictify(self):
		return {
			'id': self.id,
			'mrl': self.mrl,
			'title': self.title
		}