import socket
import requests
import time
from urllib.parse import urlparse
from src.database.db_connection import get_database

def get_ip_metadata(ip):
    """Fetches Geo-IP and ASN data using the ip-api service."""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,city,as,isp"
        response = requests.get(url, timeout=5)
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
    """Main logic with integrated AUTO-CLEANUP for dead indicators."""
    db = get_database()
    if db is None: return
    collection = db["threat_indicators"]
    
    # Target records without enrichment
    targets = collection.find({"enrichment": {"$exists": False}})
    
    enriched_count = 0
    deleted_count = 0
    
    for doc in targets:
        target_ip = None
        
        if doc['type'] == 'IPv4':
            target_ip = doc['indicator']
        elif doc['type'] in ['domain', 'URL']:
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
                collection.update_one({"_id": doc["_id"]}, {"$set": {"enrichment": enrichment_data}})
                enriched_count += 1
                time.sleep(1.5) # API Rate Limit protection
        
        # --- NEW LOGIC FOR COMMIT 2: AUTO-CLEANUP ---
        elif doc['type'] in ['domain', 'URL']:
            print(f"[!] DNS Failed. Deleting dead threat: {doc['indicator']}")
            collection.delete_one({"_id": doc["_id"]})
            deleted_count += 1
                
    print(f"\n[SUCCESS] Phase 2: {enriched_count} Enriched | {deleted_count} Purged.")
    
if __name__ == "__main__":
    run_enrichment()