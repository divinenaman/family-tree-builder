from pymongo import MongoClient
import os


def get_client():
    c = MongoClient(os.environ['MONGO_URL'])
    return c['family-tree']
