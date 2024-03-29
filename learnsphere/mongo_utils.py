from pymongo import MongoClient, TEXT

class MongoDB:
    
    client = None
    db = None
    
    @staticmethod
    def initialize(uri, db_name):
        MongoDB.client = MongoClient(uri)
        MongoDB.db = MongoDB.client[db_name]
    
    def __init__(self, collection_name):
        self.collection = MongoDB.db[collection_name]

    def create(self, data):
        return self.collection.insert_one(data)

    def read(self, query={}):
        return self.collection.find(query)

    def read_column(self, column, query={}):
        return self.collection.find(query, {'_id': 0, column: 1})
    
    def update(self, query, data):
        return self.collection.update_one(query, {'$set': data})

    def delete(self, query):
        return self.collection.delete_one(query)
    
    def search(self, searchTxt):
        pattern = f"(?i){searchTxt}"
        return self.collection.find({
            "$or": [
                {"course_name": {"$regex": pattern}},
                {"description": {"$regex": pattern}},
                {"topics": {"$regex": pattern}}
            ]
        })
        