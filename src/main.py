import sys
import os
# Ensures the project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.otx_scraper import OTXScraper
from src.scrapers.phishtank_scraper import PhishTankScraper
from src.scrapers.abuseipdb_scraper import AbuseIPDBScraper
from src.processors.enricher import run_enrichment 

def main():
    print("="*60)
    print("      CYBER-TIP PLATFORM: INGESTION & ENRICHMENT ")
    print("="*60)

    # --- PHASE 1: INGESTION ---
    print("\n[*] Initializing OSINT Scrapers...")
    
    # Initialize and run each scraper
    try:
        otx = OTXScraper()
        otx.run()
        
        abuse = AbuseIPDBScraper()
        abuse.run()
        
        phish = PhishTankScraper()
        phish.run()
        print("\n[SUCCESS] Phase 1: Data Ingestion Complete.")
    except Exception as e:
        print(f"[-] Ingestion Error: {e}")

    # --- PHASE 2: ENRICHMENT ---
    print("\n[*] Starting Phase 2: Geo-IP & DNS Enrichment...")
    run_enrichment() 

    print("\n" + "="*60)
    print("          PIPELINE EXECUTION FINISHED ")
    print("="*60)

if __name__ == "__main__":
    main()