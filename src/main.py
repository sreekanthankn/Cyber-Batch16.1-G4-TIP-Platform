import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.scrapers import otx_scraper, abuseipdb_scraper, phishtank_scraper
from src.processors.normalizer import normalize_data, save_to_db

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
        raw_indicators = run_func() # Get data from scraper
        
        saved_count = 0
        for item in raw_indicators:
            # Sreekanth's Normalizer in action:
            clean_doc = normalize_data(item, source_name)
            if clean_doc:
                if save_to_db(clean_doc):
                    saved_count += 1
        
        print(f"[+] {source_name}: Successfully normalized and saved {saved_count} records.")

    print("\n[SUCCESS] Week 2 Integration Complete.")

if __name__ == "__main__":
    main()
