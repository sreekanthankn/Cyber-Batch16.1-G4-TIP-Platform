import datetime
from src.database.db_connection import get_database

def normalize_data(raw_data, source_name):
    """
    Standardizes raw threat data into the Cyber-TIP unified schema.
    [cite: 51, 71]
    """
    # Mapping raw data to the Team's Standard Fields 
    normalized_doc = {
        "indicator": raw_data.get("indicator") or raw_data.get("ipAddress") or raw_data.get("url"),
        "type": raw_data.get("type", "Unknown"),
        "source": source_name,
        "risk_score": int(raw_data.get("risk_score", 0)), 
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }

    # Data Validation
    if not normalized_doc["indicator"]:
        return None

    return normalized_doc

def save_to_db(normalized_doc):
    """Saves the standardized document to the threat_indicators collection."""
    db = get_database()
    if db is None: # This is the correct way for PyMongo:
        return False
    
    collection = db["threat_indicators"] # [cite: 70]
    
    # Duplicate prevention logic [cite: 30]
    existing = collection.find_one({"indicator": normalized_doc["indicator"]})
    if not existing:
        collection.insert_one(normalized_doc)
        return True
    return False
