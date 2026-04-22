import sys
import os
# Ensure the root directory is in the path so imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.db_connection import get_database

def check_db_status():
    """
    Checks the status of the threat intelligence database and 
    displays statistics for each team member's source.
    """
    db = get_database()
    if db is None:
        print("\n[-] STATUS: CONNECTION FAILED")
        print("Please check your .env file and MongoDB service.")
        return

    # Standard Collection Name defined in Week 2 Workflow
    collection = db["threat_indicators"]
    
    # Get overall statistics
    total_count = collection.count_documents({})
    
    print("\n" + "="*40)
    print(" CYBER-TIP DATABASE STATUS CHECK")
    print("="*40)
    print(f"[*] Total Indicators: {total_count}")
    print("-" * 40)

    # Break down by source to check individual progress
    sources = ["AlienVault OTX", "PhishTank", "AbuseIPDB"]
    
    for source in sources:
        count = collection.count_documents({"source": source})
        print(f" [>] {source.ljust(15)} : {count} records")

    print("-" * 40)
    
    # Show the 3 most recent entries to verify field names
    if total_count > 0:
        print("[*] Recent Ingestions (Schema Check):")
        for doc in collection.find().sort("timestamp", -1).limit(3):
            print(f" - [{doc.get('source')}] {doc.get('indicator')} ({doc.get('type')})")
    else:
        print("[!] Database is currently empty.")
    
    print("="*40 + "\n")

if __name__ == "__main__":
    check_db_status()
