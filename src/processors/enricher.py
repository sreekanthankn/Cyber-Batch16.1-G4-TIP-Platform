import socket
import requests
import time
from urllib.parse import urlparse
from src.database.db_connection import get_database

def get_ip_metadata(ip):
    """Fetches Geo-IP and ASN data using the ip-api service."""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,city,as,isp"
        # Reduced timeout to 2 seconds to keep the UI snappy
        response = requests.get(url, timeout=2) 
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[-] Enrichment API error for {ip}: {e}")
    return None

def resolve_to_ip(indicator, indicator_type):
    """Converts a domain or URL into an IPv4 address via DNS lookup."""
    try:
        if indicator_type == 'URL':
            domain = urlparse(indicator).netloc
        else:
            domain = indicator
        return socket.gethostbyname(domain)
    except Exception:
        return None

def run_enrichment():
    """Main logic optimized for GUI performance."""
    db = get_database()
    if db is None: 
        return
        
    collection = db["threat_indicators"]
    
    # MODIFICATION 1: Limit to 5 records for the demo to ensure it finishes quickly
    # This prevents the 120-second timeout in app.py from triggering
    targets = collection.find({
        "enrichment": {"$exists": False},
        "risk_score": {"$gte": 90} 
    }).limit(5) 
    
    enriched_count = 0
    deleted_count = 0
    
    print("\n" + "="*50)
    print(" WEEK 3: ENRICHMENT & DATA HYGIENE PHASE")
    print("="*50)

    for doc in targets:
        target_ip = None
        
        if doc['type'] == 'IPv4':
            target_ip = doc['indicator']
        elif doc['type'] in ['domain', 'URL']:
            print(f"[*] Resolving DNS for {doc['indicator']}...")
            target_ip = resolve_to_ip(doc['indicator'], doc['type'])

        if target_ip:
            metadata = get_ip_metadata(target_ip)
            if metadata and metadata.get('status') == 'success':
                enrichment_data = {
                    "resolved_ip": target_ip,
                    "country": metadata.get("country", "Unknown"),
                    "city": metadata.get("city", "Unknown"),
                    "asn": metadata.get("as", "Unknown"),
                    "isp": metadata.get("isp", "Unknown")
                }
                
                collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"enrichment": enrichment_data}}
                )
                enriched_count += 1
                
                # MODIFICATION 2: Reduced sleep to 0.5s for the demo
                # 2.0s is too slow for a real-time progress bar experience
                time.sleep(0.5) 
            else:
                print(f"[-] Skipping {target_ip} due to API limit.")
        
        elif doc['type'] in ['domain', 'URL']:
            print(f"[!] DNS Failed. Purging: {doc['indicator']}")
            collection.delete_one({"_id": doc["_id"]})
            deleted_count += 1
                
    print("-" * 50)
    print(f"[SUCCESS] {enriched_count} Enriched | {deleted_count} Purged.")
    print("="*50 + "\n")

    # MODIFICATION 3: Force close connection to ensure the subprocess ends
    try:
        db.client.close() 
    except:
        pass

if __name__ == "__main__":
    run_enrichment()
