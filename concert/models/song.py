class Song():
    def __init__(self, mrl, title, duration, thumbnail, played_by):
        self.mrl = mrl
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.played_by = played_by

    def dictify(self):
        return {
            'mrl': self.mrl,
            'title': self.title,
            'duration': self.duration,
            'thumbnail': self.thumbnail,
            'playedby': self.played_by
        }
