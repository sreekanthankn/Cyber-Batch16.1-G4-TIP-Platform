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
