import socket
import requests
import time
from urllib.parse import urlparse
from src.database.db_connection import get_database

def get_ip_metadata(ip):
    """Fetches Geo-IP and ASN data using the ip-api service."""
    try:
        # Using ip-api.com (Free tier: 45 requests per minute)
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
            # Extract domain from URL (e.g., https://malicious.com/path -> malicious.com)
            domain = urlparse(indicator).netloc
        else:
            domain = indicator # It's already a domain string
            
        return socket.gethostbyname(domain)
    except Exception:
        # This occurs if the domain is dead or the DNS lookup fails
        return None

def run_enrichment():
    """Main logic to enrich indicators and purge unresolvable (dead) threats."""
    db = get_database()
    if db is None: 
        print("[-] Database connection failed. Aborting enrichment.")
        return
        
    collection = db["threat_indicators"]
    
    # Target any record that does not have an 'enrichment' block yet
    targets = collection.find({
        "enrichment": {"$exists": False},
        "risk_score": {"$gte": 90} 
    }).limit(100) # Process in smaller batches of 100
    
    enriched_count = 0
    deleted_count = 0
    
    print("\n" + "="*50)
    print(" WEEK 3: ENRICHMENT & DATA HYGIENE PHASE")
    print("="*50)

    for doc in targets:
        target_ip = None
        
        # 1. Identify or Resolve the IP
        if doc['type'] == 'IPv4':
            target_ip = doc['indicator']
        elif doc['type'] in ['domain', 'URL']:
            print(f"[*] Resolving DNS for {doc['type']}: {doc['indicator']}")
            target_ip = resolve_to_ip(doc['indicator'], doc['type'])

        # 2. If IP found, perform Geo-IP/ASN Enrichment
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
                # Sleep to respect the 45 req/min API rate limit
                time.sleep(2.0)
            else:
                print(f"[-] API limit or timeout for {target_ip}. Skipping for now...")
        
        # 3. AUTO-CLEANUP: If DNS lookup failed for a Domain/URL, delete it
        elif doc['type'] in ['domain', 'URL']:
            print(f"[!] DNS Resolution Failed (NXDOMAIN). Deleting dead threat: {doc['indicator']}")
            collection.delete_one({"_id": doc["_id"]})
            deleted_count += 1
                
    print("-" * 50)
    print(f"[SUCCESS] Processed: {enriched_count} Enriched | {deleted_count} Purged.")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_enrichment()
