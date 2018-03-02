from flask_login import UserMixin

class Song:
    def __init__(self, mrl, title, url, duration, thumbnail):
        self.mrl = mrl
        self.title = title
        self.url = url
        self.duration = duration
        self.thumbnail = thumbnail

    def dictify(self):
        return {
            'url': self.url,
            'mrl': self.mrl,
            'title': self.title,
            'duration': self.duration,
            'thumbnail': self.thumbnail
        }


class User(UserMixin):
    def __init__(self, uid, first_name, last_name):
        self.uid = str(uid)
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return self.uid

    def get_by_id(db, uid):
        return db.Users.find_one({'uid': uid})
