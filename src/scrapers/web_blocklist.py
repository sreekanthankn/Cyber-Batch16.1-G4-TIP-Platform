import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.database.db_setup import get_db_connection

def scrape_blocklist_de():
    """Scrape real-time attack logs from blocklist.de"""
    url = "https://www.blocklist.de/en/export.html" # Focus on their export text feeds
    target_url = "https://lists.blocklist.de/lists/all.txt"
    
    db = get_db_connection()
    if db is None: return

    print(f"🌐 Scraping official blocklist from {target_url}...")
    
    try:
        response = requests.get(target_url, timeout=10)
        if response.status_code == 200:
            # The list is a plain text file with one IP per line
            ips = response.text.splitlines()
            
            count = 0
            for ip in ips[:50]:  # Limiting to top 50 for initial ingestion
                threat_data = {
                    "indicator": ip.strip(),
                    "type": "IPv4",
                    "source": "Blocklist.de",
                    "risk_score": 90,  # Highly reliable as these are active attackers
                    "category": "SSH/Web Attackers",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                # Upsert into MongoDB
                db.malicious_indicators.update_one(
                    {"indicator": threat_data["indicator"]}, 
                    {"$set": threat_data}, 
                    upsert=True
                )
                count += 1
            print(f"✅ Successfully ingested {count} IPs from Blocklist.de")
        else:
            print(f"❌ Failed to reach blocklist. Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error during web scraping: {e}")

if __name__ == "__main__":
    scrape_blocklist_de()
