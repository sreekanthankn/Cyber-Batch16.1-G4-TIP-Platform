import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.database.db_connection import get_database

load_dotenv()

def fetch_openphish_data():
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

def save_indicators(urls):
    db = get_database()
    if db is None:
        print('[-] Database connection failed.')
        return
    collection = db['threat_indicators']
    saved = 0
    skipped = 0
    for url in urls[:100]:
        existing = collection.find_one({'indicator': url})
        if not existing:
            doc = {
                'indicator': url,
                'type': 'URL',
                'source': 'PhishTank',
                'risk_score': 90,
                'timestamp': datetime.now(timezone.utc)
            }
            collection.insert_one(doc)
            saved += 1
        else:
            skipped += 1
    print(f'[+] Saved: {saved} | Skipped: {skipped}')

def run():
    print('=' * 50)
    print(' PhishTank Scraper (OpenPhish) - Week 2')
    print('=' * 50)
    urls = fetch_openphish_data()
    if urls:
        save_indicators(urls)
    print('[*] Scraper finished.')

if __name__ == '__main__':
    run()
