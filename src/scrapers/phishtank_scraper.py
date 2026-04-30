import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

import requests
import socket
from datetime import datetime, timezone
from src.database.db_connection import get_database

BRAND_KEYWORDS = {
    "paypal": "PayPal",
    "microsoft": "Microsoft",
    "apple": "Apple",
    "google": "Google",
    "amazon": "Amazon",
    "netflix": "Netflix",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "sbi": "SBI",
    "hdfc": "HDFC Bank",
    "icici": "ICICI Bank",
    "bank": "Generic Bank",
    "chase": "Chase Bank",
    "wellsfargo": "Wells Fargo",
    "coinbase": "Coinbase",
    "binance": "Binance",
    "steam": "Steam",
    "linkedin": "LinkedIn",
    "twitter": "Twitter",
    "whatsapp": "WhatsApp",
}

def detect_brand(url):
    url_lower = url.lower()
    for keyword, brand_name in BRAND_KEYWORDS.items():
        if keyword in url_lower:
            return brand_name
    return "Unknown"

def get_ip_from_url(url):
    try:
        domain = url.split("//")[-1].split("/")[0].split(":")[0]
        ip = socket.gethostbyname(domain)
        return ip
    except Exception:
        return "Unresolved"

def fetch_openphish_data():
    print("[*] Fetching phishing URLs from OpenPhish...")
    try:
        response = requests.get("https://openphish.com/feed.txt", timeout=30)
        if response.status_code == 200:
            urls = response.text.strip().split("\n")
            print(f"[+] Fetched {len(urls)} phishing URLs.")
            return urls
        else:
            print(f"[-] Failed. Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"[-] Error: {e}")
        return []

def save_indicators(urls):
    db = get_database()
    if db is None:
        print("[-] Database connection failed.")
        return

    collection = db["threat_indicators"]
    saved = 0
    updated = 0

    for url in urls[:100]:
        target_brand = detect_brand(url)
        resolved_ip = get_ip_from_url(url)

        enrichment_data = {
            "target_brand": target_brand,
            "resolved_ip": resolved_ip,
            "enriched_at": datetime.now(timezone.utc)
        }

        existing = collection.find_one({"indicator": url})

        if not existing:
            doc = {
                "indicator": url,
                "type": "URL",
                "source": "PhishTank",
                "risk_score": 90,
                "timestamp": datetime.now(timezone.utc),
                "enrichment": enrichment_data
            }
            collection.insert_one(doc)
            saved += 1
            print(f"  [+] NEW: {url[:50]} | Brand: {target_brand}")
        else:
            # Force update enrichment on ALL existing records
            collection.update_one(
                {"indicator": url},
                {"$set": {"enrichment": enrichment_data}}
            )
            updated += 1
            print(f"  [~] UPDATED: {url[:50]} | Brand: {target_brand}")

    print(f"\n[*] Saved: {saved} | Updated: {updated}")

def run():
    print("=" * 50)
    print(" PhishTank Scraper (OpenPhish) - Week 3")
    print(" Brand Attribution & DNS Resolution")
    print("=" * 50)
    urls = fetch_openphish_data()
    if urls:
        save_indicators(urls)
    print("[*] Scraper finished.")

if __name__ == "__main__":
    run()
