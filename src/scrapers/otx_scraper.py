# otx_scraper.py
# Week 2 - AlienVault OTX Scraper
# Extracts IPs and URLs from OTX pulses and saves to MongoDB
# Contributor: Amaan Roshan

import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

# Add project root to path so we can import db_connection
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

# Load API keys from .env file
load_dotenv()
OTX_API_KEY = os.getenv("OTX_API_KEY")
BASE_URL = "https://otx.alienvault.com/api/v1"

def fetch_pulses():
    """Fetch latest threat pulses from AlienVault OTX."""
    url = f"{BASE_URL}/pulses/subscribed"
    headers = {"X-OTX-API-KEY": OTX_API_KEY}

    print("[*] Connecting to AlienVault OTX...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        pulses = response.json().get("results", [])
        print(f"[+] Fetched {len(pulses)} threat pulses.")
        return pulses
    else:
        print(f"[-] Failed to fetch. Status: {response.status_code}")
        return []

def extract_indicators(pulses):
    """Extract IPs and URLs from pulses into standardized format."""
    indicators = []

    for pulse in pulses:
        for indicator in pulse.get("indicators", []):
            itype = indicator.get("type", "")

            # Only extract IPv4 and URLs
            if itype in ["IPv4", "URL", "domain", "hostname"]:
                doc = {
                    "indicator": indicator.get("indicator", ""),
                    "type": itype,
                    "source": "AlienVault OTX",
                    "risk_score": 90 if itype == "IPv4" else 80 if itype == "URL" else 70,
                    "timestamp": datetime.now(timezone.utc),
                    "pulse_name": pulse.get("name", ""),
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
        # Check for duplicates based on indicator value
        existing = collection.find_one({"indicator": doc["indicator"]})
        if not existing:
            collection.insert_one(doc)
            saved += 1
        else:
            skipped += 1

    print(f"[+] Saved: {saved} new indicators.")
    print(f"[~] Skipped: {skipped} duplicates.")

def run():
    """Main function to run the OTX scraper."""
    print("=" * 50)
    print("  AlienVault OTX Scraper - Week 2")
    print("=" * 50)
    pulses = fetch_pulses()
    if pulses:
        indicators = extract_indicators(pulses)
        if indicators:
            save_indicators(indicators)
    print("[*] OTX Scraper finished.")

if __name__ == "__main__":
    run()
