from src.database.db_connection import get_database

def check_status():
    db = get_database()
    if db is None: return
    
    collection = db["threat_indicators"]
    
    total = collection.count_documents({})
    enriched = collection.count_documents({"enrichment": {"$exists": True}})
    pending = collection.count_documents({"enrichment": {"$exists": False}})
    
    print("\n" + "="*30)
    print(" WEEK 3 ENRICHMENT STATUS ")
    print("="*30)
    print(f"Total Records:    {total}")
    print(f"Enriched IPs:     {enriched}")
    print(f"Pending IPs:      {pending}")
    print("="*30 + "\n")

    # Show a sample of an enriched record to prove it works
    sample = collection.find_one({"enrichment": {"$exists": True}})
    if sample:
        print(f"[!] Sample Enrichment for {sample['indicator']}:")
        print(f"  - Country: {sample['enrichment'].get('country')}")
        print(f"  - ASN:     {sample['enrichment'].get('asn')}")

if __name__ == "__main__":
    check_status()