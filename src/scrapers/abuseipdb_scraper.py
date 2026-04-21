import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.database.db_connection import get_database

load_dotenv()

API_KEY = os.getenv("VT_API_KEY")

db = get_database()
collection = db["threat_indicators"]

def fetch_ip_data(ip):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"

    headers = {
        "x-apikey": API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error:", response.text)
        return None

    data = response.json()
    stats = data["data"]["attributes"]["last_analysis_stats"]

    malicious = stats.get("malicious", 0)

    return {
        "indicator": ip,
        "type": "IPv4",
        "source": "VirusTotal",
        "risk_score": malicious * 10,
        "timestamp": datetime.utcnow()
    }

def main():
    ip_list = ["8.8.8.8", "1.1.1.1"]

    results = []

    for ip in ip_list:
        result = fetch_ip_data(ip)
        if result:
            results.append(result)

    if results:
        collection.insert_many(results)
        print("Data inserted successfully")

if __name__ == "__main__":
    main()