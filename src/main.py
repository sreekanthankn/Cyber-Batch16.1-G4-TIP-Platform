import sys
import os
import threading
import webbrowser
import time
from flask import Flask

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import your modules
from src.scrapers import otx_scraper, abuseipdb_scraper, phishtank_scraper
from src.processors.normalizer import normalize_data, save_to_db
from src.processors.enricher import run_enrichment

def main():
    print("=" * 60)
    print("  CYBER-TIP PLATFORM: NORMALIZED INGESTION")
    print("=" * 60)

    scraper_list = [
        (otx_scraper.run, "AlienVault OTX"),
        (abuseipdb_scraper.run, "AbuseIPDB"),
        (phishtank_scraper.run, "PhishTank")
    ]

    for run_func, source_name in scraper_list:
        print(f"[*] Extracting from {source_name}...")
        raw_indicators = run_func() 
        
        saved_count = 0
        # Limit processing to 10 items per source for the demo to prevent hangs
        for item in raw_indicators[:10]: 
            clean_doc = normalize_data(item, source_name)
            if clean_doc:
                if save_to_db(clean_doc):
                    saved_count += 1
        
        print(f"[+] {source_name}: Normalized and saved {saved_count} records.")

    print("\n[SUCCESS] Week 2 Integration Complete.")
    print("\n[*] Starting Week 3 Enrichment Phase...")
    
    # CRITICAL: We run enrichment but we MUST ensure it doesn't loop forever
    # Ensure your run_enrichment() function has a limit=5 inside its MongoDB query
    run_enrichment()

    print("\n" + "="*60)
    print("      ✅ DATA PREPARATION COMPLETE")
    print("="*60)
    
    # IMPORTANT: When running via the Dashboard GUI, 
    # we exit here so the GUI receives the final output.
    sys.exit(0) 

if __name__ == "__main__":
    main()
