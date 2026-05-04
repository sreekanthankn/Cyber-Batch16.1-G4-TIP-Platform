import sys
import os
import threading
import webbrowser
import time
<<<<<<< Updated upstream
from src.api.app import app # Import your Flask app
=======
from flask import Flask
>>>>>>> Stashed changes

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

<<<<<<< Updated upstream
from src.scrapers import otx_scraper, abuseipdb_scraper, phishtank_scraper
from src.processors.normalizer import normalize_data, save_to_db
from src.processors.enricher import run_enrichment  # <--- Crucial for Week 3
def start_api():
    """Function to run the Flask API in a separate thread."""
    # We turn off debug mode and reloader to prevent threading conflicts
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
=======
# Import your modules
from src.scrapers import otx_scraper, abuseipdb_scraper, phishtank_scraper
from src.processors.normalizer import normalize_data, save_to_db
from src.processors.enricher import run_enrichment

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        raw_indicators = run_func() # Get data from scraper
        
        saved_count = 0
        for item in raw_indicators:
            # Sreekanth's Normalizer in action:
=======
        raw_indicators = run_func() 
        
        saved_count = 0
        # Limit processing to 10 items per source for the demo to prevent hangs
        for item in raw_indicators[:10]: 
>>>>>>> Stashed changes
            clean_doc = normalize_data(item, source_name)
            if clean_doc:
                if save_to_db(clean_doc):
                    saved_count += 1
        
<<<<<<< Updated upstream
        print(f"[+] {source_name}: Successfully normalized and saved {saved_count} records.")

    print("\n[SUCCESS] Week 2 Integration Complete.")
    print("\n[*] Starting Week 3 Enrichment Phase...")
    run_enrichment()
    print("\n" + "="*60)
    print("       🚀 LAUNCHING CYBER-TIP DASHBOARD")
    print("="*60)

    # 1. Start the Flask API in the background
    api_thread = threading.Thread(target=start_api)
    api_thread.daemon = True # This ensures the API stops when you close the terminal
    api_thread.start()

    # 2. Give the API 2 seconds to warm up
    time.sleep(2)

    # 3. Automatically open the browser to your new indicators endpoint
    url = "http://127.0.0.1:5000/api/v1/indicators"
    print(f"[*] Opening dashboard at: {url}")
    webbrowser.open(url)

    # 4. Keep the main script alive so the API stays running
    print("\n[INFO] Press Ctrl+C to stop the API server and exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down Cyber-TIP Platform. Goodbye!")
=======
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

>>>>>>> Stashed changes
if __name__ == "__main__":
    main()
