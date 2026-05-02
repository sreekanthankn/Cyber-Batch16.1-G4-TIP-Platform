from src.database.db_connection import get_database

def check_progress():
    db = get_database()
    collection = db["threat_indicators"]
    
    total = collection.count_documents({})
    enriched = collection.count_documents({"enrichment": {"$exists": True}})
    pending = collection.count_documents({"enrichment": {"$exists": False}, "type": "IPv4"})
    
    print(f"--- WEEK 3 ENRICHMENT STATUS ---")
    print(f"Total Records:      {total}")
    print(f"Enriched IPs:       {enriched}")
    print(f"Pending IPs:        {pending}")
    
    if enriched > 0:
        sample = collection.find_one({"enrichment": {"$exists": True}})
        print(f"\n[!] Sample Enrichment for {sample['indicator']}:")
        print(f"    - Country: {sample['enrichment']['country']}")
        print(f"    - ASN:     {sample['enrichment']['asn']}")

if __name__ == "__main__":
    check_progress()
