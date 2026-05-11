import os
import pymongo
from dotenv import load_dotenv

# Load environment variables from a .env file for security
load_dotenv()

def get_database():
    """
    Establishes a connection to the local MongoDB instance.
    """
    # MongoDB connection string - Defaulting to localhost:27017
    CONNECTION_STRING = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = "CyberTIP_Platform"

    try:
        # Initialize the client with a 5-second timeout
        client = pymongo.MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=5000)
        
        # Ping the server to verify the connection is alive
        client.admin.command('ping')
        
        db = client[DB_NAME]
        print(f"[SUCCESS] Connected to MongoDB: {DB_NAME}")
        return db
        
    except Exception as e:
        print(f"[ERROR] Could not connect to MongoDB: {e}")
        return None

if __name__ == "__main__":
    # Self-test block to verify the environment
    print("Testing MongoDB connection...")
    database = get_database()
    if database is not None:
        print("Database connection test passed. Environment is ready.")
    else:
        print("Database connection test failed. Please check your 'mongod' service.")
