<<<<<<< Updated upstream
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.database.db_connection import get_database

load_dotenv()

API_KEY = os.getenv("ABUSEIPDB_API_KEY")
BASE_URL = "https://api.abuseipdb.com/api/v2/check"

HEADERS = {
    "Key": API_KEY,
    "Accept": "application/json"
}


def fetch_ip_data(ip):
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"[ERROR] API Error: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return None


def process_ip(ip):
    db = get_database()
    if db is None:
        return

    collection = db["indicators"]

    data = fetch_ip_data(ip)
    if not data:
        return

    # ✅ REQUIRED FIELDS
    total_reports = data.get("totalReports", 0)
    confidence_score = data.get("abuseConfidenceScore", 0)
    last_reported = data.get("lastReportedAt")

    if last_reported:
        last_reported = datetime.fromisoformat(last_reported.replace("Z", ""))

    # ✅ ENRICHMENT BLOCK (IMPORTANT)
    enrichment_data = {
        "source": "AbuseIPDB",
        "abuseConfidenceScore": confidence_score,
        "totalReports": total_reports,
        "lastReportedAt": last_reported
    }

    # ✅ BASE RISK SCORE (can be improved later)
    risk_score = confidence_score  # simple mapping for now

    record = {
        "indicator": ip,
        "type": "ip",
        "risk_score": risk_score,
        "enrichment": enrichment_data,
        "updated_at": datetime.utcnow()
    }

    collection.update_one(
        {"indicator": ip},
        {"$set": record},
        upsert=True
    )

    print(f"[SUCCESS] {ip} | Confidence: {confidence_score} | Reports: {total_reports}")


if __name__ == "__main__":
    test_ips = ["8.8.8.8", "185.220.101.1"]

    for ip in test_ips:
        process_ip(ip)
=======
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('ABUSEIPDB_API_KEY')

def run():
    print("[*] Connecting to AbuseIPDB...")
    url = 'https://api.abuseipdb.com/api/v2/blacklist'
    headers = {'Key': API_KEY, 'Accept': 'application/json'}
    params = {
    'maxAgeInDays': '1',  # Only fetch IPs reported in the last 24 hours
    'confidenceMinimum': '90',
    'limit': '50'         # Get a manageable sample of 50 IPs
    }

    response = requests.get(url, headers=headers, params=params)
    indicators = []

    if response.status_code == 200:
        data = response.json().get('data', [])
        for entry in data:
            indicators.append({
                "indicator": entry.get('ipAddress'),
                "type": "IPv4",
                "source": "AbuseIPDB",
                "risk_score": entry.get('abuseConfidenceScore', 95),
                "metadata": {"total_reports": entry.get('totalReports')}
            })
        print(f"[+] AbuseIPDB: Extracted {len(indicators)} high-confidence IPs.")
    return indicators
>>>>>>> Stashed changes
