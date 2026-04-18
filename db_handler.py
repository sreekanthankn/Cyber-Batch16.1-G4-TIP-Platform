# db_handler.py
# Week 1 - Database Handler: Saves threat data into MongoDB

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def get_database():
    """Connect to MongoDB and return the threat database."""
    client = MongoClient(MONGO_URI)
    db = client["threat_intel_db"]
    return db

def save_pulses(pulses):
    """Save threat pulses into MongoDB, avoiding duplicates."""
    db = get_database()
    collection = db["threat_indicators"]

    saved = 0
    skipped = 0

    for pulse in pulses:
        # Use pulse ID to avoid saving duplicates
        existing = collection.find_one({"id": pulse["id"]})
        if not existing:
            collection.insert_one(pulse)
            saved += 1
        else:
            skipped += 1

    print(f"[+] Saved: {saved} new threat pulses.")
    print(f"[~] Skipped: {skipped} duplicates.")

def show_saved_threats():
    """Display threats saved in MongoDB."""
    db = get_database()
    collection = db["threat_indicators"]

    count = collection.count_documents({})
    print(f"\n[*] Total threats in database: {count}")
    print("-" * 50)

    for threat in collection.find().limit(5):
        print(f"  Name: {threat.get('name', 'N/A')}")
        print(f"  Author: {threat.get('author_name', 'N/A')}")
        print(f"  Created: {threat.get('created', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    show_saved_threats()
