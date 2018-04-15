from pymongo import MongoClient

class MongoConnector():
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.concert

    def remove_user_session(self, user):
        self.db.Users.delete_many({"uid": user.uid})

    def add_user_session(self, user):
        self.db.Users.insert_one(user.__dict__)

    def get_user_by_id(self, uid):
        return self.db.Users.find_one({'uid': uid})