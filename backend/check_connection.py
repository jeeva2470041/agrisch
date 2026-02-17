from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

import certifi

MONGO_URI = os.getenv("MONGO_URI")
print(f"Connecting to: {MONGO_URI.split('@')[1]}") # Print just the host part for privacy

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000, tlsCAFile=certifi.where())
    client.admin.command('ping')
    print("✅ Connection Successful!")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
