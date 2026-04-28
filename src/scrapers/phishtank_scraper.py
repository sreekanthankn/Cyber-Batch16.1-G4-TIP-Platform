import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

load_dotenv()

def fetch_openphish_data():
    """Fetches phishing URLs from the OpenPhish public feed."""
    print('[*] Fetching phishing URLs from OpenPhish...')
    url = 'https://openphish.com/feed.txt'
    response = requests.get(url)
    if response.status_code == 200:
        urls = response.text.strip().split('\n')
        print(f'[+] Fetched {len(urls)} phishing URLs.')
        return urls
    else:
        print(f'[-] Failed. Status: {response.status_code}')
        return []

def run():
    """Returns standardized data to the main orchestrator."""
    print('=' * 50)
    print(' PhishTank Scraper (OpenPhish) - Week 2')
    print('=' * 50)
    
    urls = fetch_openphish_data()
    results = []

    if urls:
        # We only take 100 for normalization
        for url in urls[:100]:
            doc = {
                'indicator': url,
                'type': 'URL',
                'source': 'PhishTank',
                'risk_score': 90,
                'timestamp': datetime.now(timezone.utc)
            }
            results.append(doc)
    
    print(f'[*] Prepared {len(results)} indicators for normalization.')
    return results
class PhishTankScraper:
    """Class wrapper for main.py compatibility."""
    
    def run(self):
        db = get_database()
        if db is None:
            print("[-] Database connection failed.")
            return
        collection = db["threat_indicators"]
        urls = fetch_openphish_data()
        saved = 0
        skipped = 0
        for url in urls[:100]:
            existing = collection.find_one({"indicator": url})
            if not existing:
                doc = {
                    "indicator": url,
                    "type": "URL",
                    "source": "PhishTank",
                    "risk_score": 90,
                    "timestamp": datetime.now(timezone.utc),
                    "enrichment": {
                        "target_brand": "N/A",
                        "country": "N/A",
                        "asn": "N/A",
                        "isp": "N/A"
                    }
                }
                collection.insert_one(doc)
                saved += 1
            else:
                skipped += 1
        print(f"[+] PhishTank - Saved: {saved} | Skipped: {skipped}")
