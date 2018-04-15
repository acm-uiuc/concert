from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, uid, first_name, last_name):
        self.uid = str(uid)
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return self.uid