import os
import pymongo
from dotenv import load_dotenv
from pymongo.errors import CollectionInvalid

# Load variables from .env
load_dotenv()

def get_db_connection():
    """Establish and return a NoSQL database connection with schema validation"""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "ThreatIntel_DB")
    
    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        
        # Schema Validation Logic
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["indicator", "type", "source", "timestamp"],
                "properties": {
                    "indicator": {"bsonType": "string"},
                    "type": {"enum": ["IPv4", "IPv6", "Domain"]},
                    "source": {"bsonType": "string"},
                    "risk_score": {"bsonType": "int", "minimum": 0, "maximum": 100},
                    "timestamp": {"bsonType": "string"}
                }
            }
        }

        try:
            db.create_collection("malicious_indicators", validator=validator)
            print("✅ Collection 'malicious_indicators' created with validation.")
        except CollectionInvalid:
            print("ℹ️ Collection already exists. Ensuring validation is active.")

        # Test connection
        client.server_info() 
        print(f"🚀 Successfully connected to {db_name}")
        return db
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

if __name__ == "__main__":
    get_db_connection()