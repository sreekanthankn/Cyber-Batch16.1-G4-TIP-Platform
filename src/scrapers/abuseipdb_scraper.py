import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('ABUSEIPDB_API_KEY')

def run():
    print("[*] Connecting to AbuseIPDB...")
    url = 'https://api.abuseipdb.com/api/v2/blacklist'
    headers = {'Key': API_KEY, 'Accept': 'application/json'}
    params = {'confidenceMinimum': 90} # Only fetch high-confidence threats

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