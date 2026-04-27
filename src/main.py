import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.scrapers import otx_scraper, abuseipdb_scraper, phishtank_scraper
from src.processors.normalizer import normalize_data, save_to_db


from src.scrapers.otx_scraper import OTXScraper
from src.scrapers.phishtank_scraper import PhishTankScraper
from src.scrapers.abuseipdb_scraper import AbuseIPDBScraper
from src.processors.normalizer import Normalizer
from src.processors.enricher import run_enrichment 


def main():
    print("="*50)
    print(" CYBER-TIP PLATFORM: INGESTION & ENRICHMENT ")
    print("="*50)

    # --- PHASE 1: INGESTION (Week 2 Legacy) ---
    # (Your existing scraper calls go here)
    # Example:
    # otx = OTXScraper()
    # otx.run()
    
    print("\n[SUCCESS] Phase 1: Data Ingestion Complete.")

    # --- PHASE 2: ENRICHMENT (Week 3 Commit 1) ---
    print("\n[*] Starting Phase 2: Geo-IP & DNS Enrichment...")
    run_enrichment() 

    print("\n" + "="*50)
    print(" PIPELINE EXECUTION FINISHED ")
    print("="*50)

if __name__ == "__main__":
    main()
