import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME", "publishing_system")

if not uri:
    raise RuntimeError("MONGODB_URI is not set in .env")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client[db_name]

try:
    client.admin.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print("Could not connect to DB:", e)
