# otx_scraper.py
# Week 3 - AlienVault OTX Scraper with Pulse Metadata Enrichment
# Contributor: Amaan Roshan

import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

load_dotenv()
OTX_API_KEY = os.getenv("OTX_API_KEY")
BASE_URL = "https://otx.alienvault.com/api/v1"

class OTXScraper:
    """AlienVault OTX Scraper - Extracts IPs, URLs and pulse metadata."""

    def __init__(self):
        self.db = get_database()
        self.collection = self.db["indicators"] if self.db is not None else None

    def fetch_pulses(self):
        """Fetch latest threat pulses from AlienVault OTX."""
        url = f"{BASE_URL}/pulses/subscribed"
        headers = {"X-OTX-API-KEY": OTX_API_KEY}
        print("[*] Connecting to AlienVault OTX...")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            pulses = response.json().get("results", [])
            print(f"[+] Fetched {len(pulses)} threat pulses.")
            return pulses
        else:
            print(f"[-] Failed to fetch. Status: {response.status_code}")
            return []

    def extract_indicators(self, pulses):
        """Extract IPs and URLs with pulse metadata."""
        indicators = []
        for pulse in pulses:
            for indicator in pulse.get("indicators", []):
                itype = indicator.get("type", "")
                if itype in ["IPv4", "URL", "domain", "hostname"]:
                    doc = {
                        "indicator": indicator.get("indicator", ""),
                        "type": itype,
                        "source": "AlienVault OTX",
                        "risk_score": 90 if itype == "IPv4" else 80 if itype == "URL" else 70,
                        "timestamp": datetime.now(timezone.utc),
                        "enrichment": {
                            # Week 3: Pulse metadata fields
                            "pulse_name": pulse.get("name", "N/A"),
                            "tags": pulse.get("tags", []),
                            "description": pulse.get("description", "N/A"),
                            "country": "N/A",
                            "asn": "N/A",
                            "isp": "N/A"
                        }
                    }
                    indicators.append(doc)
        print(f"[+] Extracted {len(indicators)} indicators with metadata.")
        return indicators

    def save_indicators(self, indicators):
        """Save indicators to MongoDB, skipping duplicates."""
        if self.collection is None:
            print("[-] Database connection failed. Aborting.")
            return
        saved = 0
        skipped = 0
        for doc in indicators:
            existing = self.collection.find_one({"indicator": doc["indicator"]})
            if not existing:
                self.collection.insert_one(doc)
                saved += 1
            else:
                skipped += 1
        print(f"[+] OTX - Saved: {saved} new | Skipped: {skipped} duplicates.")

    def run(self):
        """Main method called by main.py."""
        print("\n" + "="*50)
        print("  AlienVault OTX Scraper - Week 3")
        print("="*50)
        pulses = self.fetch_pulses()
        if pulses:
            indicators = self.extract_indicators(pulses)
            if indicators:
                self.save_indicators(indicators)
        print("[*] OTX Scraper finished.")
