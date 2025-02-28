import os
from pymongo import MongoClient
from dotenv import load_dotenv


class DBUtils:
    def __init__(
        self,
        server="localhost:27017",
        db_name="my_database",
        user=None,
        password=None,
        collection_name="my_collection",
    ):

        self.server = server
        self.db_name = db_name
        self.user = user
        self.password = password
        self.collection_name = collection_name

        self.client = None
        self.db = None
        self.collection = None

    def connect(self):

        if self.user and self.password:
            mongo_uri = f"mongodb://{self.user}:{self.password}@{self.server}/{self.db_name}?authSource=admin"
        else:
            mongo_uri = f"mongodb://{self.server}"

        self.client = MongoClient(mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        print(
            f"Connected to MongoDB at {mongo_uri}, using database '{self.db_name}' and collection '{self.collection_name}'"
        )

    def disconnect(self):
        self.client.close()

    def query(self, query_filter=None):

        if query_filter is None:
            query_filter = {}

        return list(self.collection.find(query_filter))

    def insert(self, doc):
        result = self.collection.insert_one(doc)
        return result.inserted_id

    def delete(self, delete_filter):
        result = self.collection.delete_many(delete_filter)
        return True
