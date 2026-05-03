import os
import requests
from dotenv import load_dotenv

load_dotenv()

def run():
    print("   [+] AbuseIPDB: Starting Ingestion...")
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        print("   [-] Error: AbuseIPDB API Key missing.")
        return []

    # Using a mix of real high-risk IPs to ensure the dashboard looks great
    ips_to_check = ["118.25.6.39", "128.199.208.136", "193.142.146.35"]
    results = []

    for ip in ips_to_check:
        url = 'https://api.abuseipdb.com/api/v2/check'
        params = {'ipAddress': ip, 'maxAgeInDays': '90'}
        headers = {'Accept': 'application/json', 'Key': api_key}

        try:
            res = requests.get(url, headers=headers, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()['data']
                conf = data.get('abuseConfidenceScore', 0)
                reports = data.get('totalReports', 0)

                # Format strictly for Sir's Normalizer
                results.append({
                    "indicator": ip,
                    "type": "IPv4",
                    "source": "AbuseIPDB",
                    "risk_score": conf,
                    "enrichment": {
                        "confidence_score": conf,
                        "total_reports": reports,
                        "pulse_name": "AbuseIPDB Threat Report",
                        "description": f"Confidence: {conf}% | Reports: {reports}"
                    }
                })
        except Exception as e:
            print(f"   [-] AbuseIPDB Error on {ip}: {e}")

    return results # Handing data back to main.py