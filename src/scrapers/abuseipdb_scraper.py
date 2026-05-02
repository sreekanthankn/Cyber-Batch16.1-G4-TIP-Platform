import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.database.db_connection import get_database

load_dotenv()

API_KEY = os.getenv("ABUSEIPDB_API_KEY")

db = get_database()
collection = db["threat_indicators"]


def fetch_ip_data(ip):
    url = "https://api.abuseipdb.com/api/v2/check"

    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Error:", response.text)
        return None

    data = response.json()["data"]

    return {
        "ip": data.get("ipAddress"),
        "source": "abuseipdb",
        "type": "IPv4",
        "timestamp": datetime.utcnow(),
        
        # 🔥 IMPORTANT (Week 3 requirement)
        "enrichment": {
            "confidence_score": data.get("abuseConfidenceScore"),
            "total_reports": data.get("totalReports")
        }
    }


def filter_high_risk(data):
    high_risk = []

    for item in data:
        score = item.get("enrichment", {}).get("confidence_score", 0)
        if score > 90:
            high_risk.append(item)

    return high_risk


def main():
    ip_list = ["8.8.8.8", "1.1.1.1"]

    results = []

    for ip in ip_list:
        result = fetch_ip_data(ip)
        if result:
            results.append(result)

    # 🔥 Apply filtering (Week 4)
    high_risk_data = filter_high_risk(results)

    if high_risk_data:
        collection.insert_many(high_risk_data)
        print("High-risk data inserted successfully")
    else:
        print("No high-risk IPs found")


if __name__ == "__main__":
    main()