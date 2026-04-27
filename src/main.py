import threading
import webbrowser
import time
import sys
import os
<<<<<<< Updated upstream
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.scrapers import otx_scraper, abuseipdb_scraper, phishtank_scraper
from src.processors.normalizer import normalize_data, save_to_db


from src.scrapers.otx_scraper import OTXScraper
from src.scrapers.phishtank_scraper import PhishTankScraper
from src.scrapers.abuseipdb_scraper import AbuseIPDBScraper
from src.processors.normalizer import Normalizer
from src.processors.enricher import run_enrichment 
=======

# Ensures the project root is in the path for module discovery
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.app import app
from src.processors.enricher import run_enrichment

def launch_api():
    """
    Runs the Flask API server.
    use_reloader is set to False to prevent the thread from spawning twice.
    """
    print("[*] Initializing Threat Intel API on port 5000...")
    app.run(port=5000, debug=False, use_reloader=False)
>>>>>>> Stashed changes


def main():
<<<<<<< Updated upstream
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
=======
    print("="*60)
    print("   CYBER-TIP PLATFORM: AUTOMATED API & ENRICHMENT ")
    print("="*60)

    # 1. Start the API Service in a background thread
    # This allows the script to continue to the next lines of code
    api_thread = threading.Thread(target=launch_api, daemon=True)
    api_thread.start()
    
    # 2. Wait for the server to initialize
    print("[*] Waiting for API stability...")
    time.sleep(2)
    
    # 3. Launch the Executive Dashboard in the default browser
    # Automatically requests the limit of 372 you verified earlier
    dashboard_url = "http://127.0.0.1:5000/api/v1/indicators?limit=372"
    print(f"[*] Launching Dashboard: {dashboard_url}")
    webbrowser.open(dashboard_url)
    
    # 4. Execute the Backend Enrichment & Hygiene Pipeline
    # This runs the Geo-IP, DNS resolution, and Auto-Cleanup logic
    print("\n[*] Starting Background Data Enrichment & Hygiene...")
    try:
        run_enrichment()
    except Exception as e:
        print(f"[-] Pipeline Error: {e}")

    print("\n" + "="*60)
    print("  SYSTEM ONLINE: API ACTIVE | DATA ENRICHED ")
    print("="*60)
>>>>>>> Stashed changes

    # Keep the main process alive so the background API thread doesn't close
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[!] Shutting down Cyber-TIP Platform...")

if __name__ == "__main__":
    main()
