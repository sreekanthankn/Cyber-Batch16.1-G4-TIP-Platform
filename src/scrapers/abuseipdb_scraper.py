import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

class AbuseIPDBScraper:
    def __init__(self):
        """Initializes the scraper and loads the API key."""
        load_dotenv()
        self.api_key = os.getenv("ABUSEIPDB_API_KEY")
        self.source_name = "AbuseIPDB"

    def fetch_abuse_data(self):
        """Fetches the latest malicious IPs from AbuseIPDB."""
        url = 'https://api.abuseipdb.com/api/v2/blacklist'
        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }
        params = {'limit': '50'}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[-] {self.source_name} Error: {response.status_code}")
            return []
        
        return response.json().get('data', [])

    def run(self):
        """Returns normalized data to the main orchestrator."""
        print(f"Starting {self.source_name} scraper...")
        raw_data = self.fetch_abuse_data()
        results = []

        for item in raw_data:
            # Standardizing fields for the normalizer
            doc = {
                "indicator": item.get("ipAddress"),
                "type": "IPv4",
                "source": self.source_name,
                "risk_score": item.get("abuseConfidenceScore", 0),
                "timestamp": datetime.now(timezone.utc)
            }
            results.append(doc)
        
        print(f"{self.source_name} scraping complete.")
        return results