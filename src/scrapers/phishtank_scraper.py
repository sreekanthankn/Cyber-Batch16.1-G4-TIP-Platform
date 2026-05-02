import requests

def run():
    print("[*] Connecting to PhishTank...")
    url = "https://data.phishtank.com/data/online-valid.json"
    
    # Standard PhishTank requests often require a User-Agent
    headers = {'User-Agent': 'phishtank/Cyber-Batch16.1-G4-TIP-Platform'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        indicators = []

        if response.status_code == 200:
            data = response.json()
            # Limit to top 100 for performance
            for entry in data[:100]:
                indicators.append({
                    "indicator": entry.get('url'),
                    "type": "URL",
                    "source": "PhishTank",
                    "risk_score": 90,
                    "metadata": {
                        "target": entry.get('target', 'Unknown'),
                        "phish_id": entry.get('phish_id')
                    }
                })
            print(f"[+] PhishTank: Extracted {len(indicators)} verified phishing URLs.")
        return indicators
    except Exception as e:
        print(f"[-] PhishTank Error: {e}")
        return []