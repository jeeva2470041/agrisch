import socket
import ssl
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

def test_tcp_connection(host, port):
    print(f"Testing TCP connection to {host}:{port}...")
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        print(f"✅ TCP connection to {host}:{port} successful!")
        return True
    except Exception as e:
        print(f"❌ TCP connection to {host}:{port} failed: {e}")
        return False

# Extract host from URI
try:
    # Basic parsing for mongodb+srv://
    if "mongodb+srv://" in mongo_uri:
        # For SRV records, we need to resolve the actual host, but let's try the cluster domain first
        # typically clustername.xxxx.mongodb.net
        clean_uri = mongo_uri.replace("mongodb+srv://", "")
        if "@" in clean_uri:
            host_part = clean_uri.split("@")[1]
        else:
            host_part = clean_uri
        
        host_base = host_part.split("/")[0].split("?")[0]
        print(f"Cluster domain: {host_base}")
        
        # We can't easily resolve SRV in python without dnspython, but we know the shard names
        # usually follow the pattern: clustername-shard-00-00.xxxx.mongodb.net
        # looking at your logs: ac-3y3wiwz-shard-00-00.dgo2kvl.mongodb.net
        
        # Let's try to connect to the one from your error log
        shard_host = "ac-3y3wiwz-shard-00-00.dgo2kvl.mongodb.net"
        if not test_tcp_connection(shard_host, 27017):
            print("\n⚠️  DIAGNOSIS: Port 27017 is blocked.")
            print("This is likely due to your VPN or Firewall blocking non-standard ports.")
            print("Try disconnecting the VPN or using a different network.")
        else:
            print("\n✅ Port 27017 is open. Proceeding to MongoDB connection...")
            try:
                client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000, tlsCAFile=certifi.where())
                client.admin.command('ping')
                print("✅ MongoDB Connection Successful!")
            except Exception as e:
                print(f"❌ MongoDB Connection Failed: {e}")

except Exception as e:
    print(f"Error parsing URI: {e}")
