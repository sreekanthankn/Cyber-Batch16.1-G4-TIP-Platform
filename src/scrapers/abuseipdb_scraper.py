import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")

def fetch_abuse_data():
    """Fetches the latest malicious IPs from AbuseIPDB."""
    url = 'https://api.abuseipdb.com/api/v2/blacklist'
    headers = {
        'Accept': 'application/json',
        'Key': API_KEY
    }
    params = {'limit': '50'}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"[-] AbuseIPDB Error: {response.status_code}")
        return []
    
    return response.json().get('data', [])

def run():
    """Returns raw data to the main orchestrator for normalization."""
    raw_data = fetch_abuse_data()
    results = []

    for item in raw_data:
        # Standardizing fields for Sreekanth's normalizer
        doc = {
            "indicator": item.get("ipAddress"),
            "type": "IPv4",
            "source": "AbuseIPDB",
            "risk_score": item.get("abuseConfidenceScore", 0),
            "timestamp": datetime.now(timezone.utc)
        }
        results.append(doc)
    
    # We return the list so main.py can pass it to normalizer.py
    return results
