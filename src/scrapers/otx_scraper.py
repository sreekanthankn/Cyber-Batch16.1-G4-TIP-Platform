import os
import requests
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure project root is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

load_dotenv()
OTX_API_KEY = os.getenv('OTX_API_KEY')
BASE_URL = 'https://otx.alienvault.com/api/v1'

def fetch_pulses():
    """Fetch latest threat pulses from AlienVault OTX."""
    url = f"{BASE_URL}/pulses/subscribed"
    headers = {'X-OTX-API-KEY': OTX_API_KEY}
    print("[*] Connecting to AlienVault OTX...")
        
    params = {'limit': '10'}  
    response = requests.get(url, headers=headers, params=params)
    

    if response.status_code == 200:
        data = response.json()
        pulses = data.get('results', [])
        print(f"[+] Fetched {len(pulses)} threat pulses.")
        return pulses
    else:
        print(f"[-] Failed to fetch. Status: {response.status_code}")
        return []  

def extract_indicators(pulses):
    """Extract IPs and URLs from pulses into standardized format."""
    indicators = []
    for pulse in pulses:
        # Extract metadata found in bytecode
        pulse_name = pulse.get('name', 'Unknown Pulse')
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for item in pulse.get('indicators', []):
            itype = item.get('type')
            # Standardizing types as seen in bytecode
            if itype in ['IPv4', 'URL', 'domain', 'hostname']:
                doc = {
                    "indicator": item.get('indicator'),
                    "type": itype,
                    "source": "AlienVault OTX",
                    "risk_score": 75,  # Default risk score found in logic
                    "timestamp": timestamp,
                    "pulse_name": pulse_name
                }
                indicators.append(doc)
    print(f"[+] Extracted {len(indicators)} indicators (IPs and URLs).")
    return indicators

def save_indicators(indicators):
    """Save indicators to MongoDB, skipping duplicates."""
    db = get_database()
    if db is None: 
        print("[-] Database connection failed. Aborting.")
        return
    
    collection = db["threat_indicators"]
    saved = 0
    skipped = 0
    
    for doc in indicators:
        # Check for duplicates before inserting
        existing = collection.find_one({"indicator": doc["indicator"]})
        if not existing:
            collection.insert_one(doc)
            saved += 1
        else:
            skipped += 1
            
    print(f"[+] Saved: {saved} new indicators.")
    print(f"[~] Skipped: {skipped} duplicates.")

def run():
    """Main function to run the OTX scraper and RETURN data for main.py."""
    print("="*50)
    print("  AlienVault OTX Scraper - Week 3 Update")
    print("="*50)
    
    pulses = fetch_pulses()
    if pulses:
        indicators = extract_indicators(pulses)
        # We save here for redundancy, but we MUST return the list
        save_indicators(indicators)
        return indicators # <--- THIS FIXES THE TypeError
    
    return [] # Return an empty list instead of None if no pulses found
if __name__ == "__main__":
    run()
