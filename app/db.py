import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME", "publishing_system")

if not uri:
    raise RuntimeError("MONGODB_URI is not set in .env")

def get_database(cluster_region: str):
    if not cluster_region:
        raise ValueError("Cluster region is required!")
    client = MongoClient(uri, server_api=ServerApi("1"))
    return client[db_name]

db = get_database()

try:
    client = MongoClient(uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    print("Connected to MongoDB")
except Exception as e:
    print("Could not connect to DB:", e)