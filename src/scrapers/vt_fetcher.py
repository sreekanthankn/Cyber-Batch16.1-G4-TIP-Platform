import os
import time
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from src.database.db_setup import get_db_connection

load_dotenv()

def fetch_vt_data():
    api_key = os.getenv("VT_API_KEY")
    db = get_db_connection()
    if db is None: return

    # For the demo, we will check a known malicious IP
    # In a real scenario, this would loop through IPs found by OTX
    targets = ["1.1.1.1", "8.8.8.8", "185.159.157.37"] 
    
    print(f"🧪 Verifying {len(targets)} targets against VirusTotal...")

    for ip in targets:
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"x-apikey": api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                stats = response.json()['data']['attributes']['last_analysis_stats']
                malicious_count = stats.get('malicious', 0)
                
                print(f"🔍 IP: {ip} | Malicious Flags: {malicious_count}")
                
                threat_data = {
                    "indicator": ip,
                    "type": "IPv4",
                    "source": "VirusTotal",
                    "risk_score": 100 if malicious_count > 10 else 50,
                    "category": "Engine Verified",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                db.malicious_indicators.update_one(
                    {"indicator": ip}, {"$set": threat_data}, upsert=True
                )
            else:
                print(f"⚠️ VT Skip: {ip} (Status {response.status_code})")
            
            # Respect Free API Rate Limits (15s sleep between requests)
            time.sleep(15) 
            
        except Exception as e:
            print(f"❌ VT Error: {e}")

    print("\n✅ VirusTotal Verification Module Finished.")

if __name__ == "__main__":
    fetch_vt_data()
