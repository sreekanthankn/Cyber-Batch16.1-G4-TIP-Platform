import os
from OTXv2 import OTXv2, IndicatorTypes
from dotenv import load_dotenv
from datetime import datetime, timezone
from src.database.db_setup import get_db_connection

load_dotenv()

def fetch_otx_indicators():
    api_key = os.getenv("OTX_API_KEY")
    otx = OTXv2(api_key)
    db = get_db_connection()
    if db is None: return

    print("🔍 Fetching specific pulses for faster ingestion...")
    
    try:
        # SEARCHING instead of getall() is much faster for a quick test
        # This looks for pulses tagged with 'malware'
        pulses = otx.search_pulses(query="malware")['results']
    except Exception as e:
        print(f"❌ API Error: {e}")
        return
    
    count = 0
    for pulse in pulses[:3]: # Only the first 3 pulses
        pulse_name = pulse.get('name', 'Unknown')
        # In search results, indicators are often in a slightly different structure
        # Let's fetch the full pulse detail for the indicators
        full_pulse = otx.get_pulse_details(pulse['id'])
        indicators = full_pulse.get('indicators', [])
        
        print(f"📦 Pulse: {pulse_name} | Found {len(indicators)} indicators")
        
        for ind in indicators:
            if ind['type'] in [IndicatorTypes.IPv4.name, IndicatorTypes.DOMAIN.name]:
                threat_data = {
                    "indicator": ind['indicator'],
                    "type": "IPv4" if ind['type'] == IndicatorTypes.IPv4.name else "Domain",
                    "source": "AlienVault OTX",
                    "risk_score": 70,
                    "category": pulse_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                db.malicious_indicators.update_one(
                    {"indicator": threat_data["indicator"]}, 
                    {"$set": threat_data}, 
                    upsert=True
                )
                count += 1
                if count % 5 == 0:
                    print(f"   📥 Ingested {count}...")

    print(f"\n✅ SUCCESS: {count} indicators added to MongoDB.")

if __name__ == "__main__":
    fetch_otx_indicators()
