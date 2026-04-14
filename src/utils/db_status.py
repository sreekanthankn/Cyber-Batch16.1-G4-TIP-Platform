from src.database.db_setup import get_db_connection

def generate_status_report():
    db = get_db_connection()
    if db is None: return

    collection = db.malicious_indicators
    
    total = collection.count_documents({})
    otx_count = collection.count_documents({"source": "AlienVault OTX"})
    vt_count = collection.count_documents({"source": "VirusTotal"})
    bl_count = collection.count_documents({"source": "Blocklist.de"})

    print("-" * 30)
    print("📊 THREAT INTELLIGENCE SUMMARY")
    print("-" * 30)
    print(f"Total Indicators:   {total}")
    print(f"AlienVault OTX:     {otx_count}")
    print(f"VirusTotal:         {vt_count}")
    print(f"Blocklist.de:       {bl_count}")
    print("-" * 30)

if __name__ == "__main__":
    generate_status_report()
