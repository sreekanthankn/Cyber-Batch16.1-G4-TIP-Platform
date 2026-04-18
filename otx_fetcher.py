# otx_fetcher.py
# Week 1 - OSINT Ingestion: Fetches threat indicators from AlienVault OTX

import os
import requests
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
OTX_API_KEY = os.getenv("OTX_API_KEY")

# AlienVault OTX base URL
BASE_URL = "https://otx.alienvault.com/api/v1"

def fetch_latest_pulses():
    """Fetch the latest threat pulses from AlienVault OTX."""
    url = f"{BASE_URL}/pulses/subscribed"
    headers = {"X-OTX-API-KEY": OTX_API_KEY}

    print("[*] Connecting to AlienVault OTX...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        pulses = data.get("results", [])
        print(f"[+] Successfully fetched {len(pulses)} threat pulses.")
        for pulse in pulses[:3]:
            print(f"    - {pulse['name']} | Indicators: {pulse.get('indicator_count', pulse.get('indicators_count', 'N/A'))}")
        return pulses
    else:
        print(f"[-] Failed to fetch data. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    fetch_latest_pulses()
