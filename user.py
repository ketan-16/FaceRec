import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["staff"]
mycol = mydb["Admin"]

class User:
    def __init__(self,_id,username,password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls,username):
        x = mycol.find_one({"Email":username},{"_id":0})
        if x:
            return cls(*x)
        return None

    @classmethod
    def find_by_id(cls,_id):
        x = mycol.find_one({"id":_id},{"_id":0})
        if x:
            return cls(*x)
        return None