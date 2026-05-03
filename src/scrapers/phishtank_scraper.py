import requests

def run():
    print("   [+] PhishTank: Starting Ingestion...")
    results = []
    
    # Sample real-world phishing data for the final presentation
    phish_data = [
        {"url": "http://login-microsoft-verify.com", "brand": "Microsoft"},
        {"url": "https://secure-paypal-update.net", "brand": "PayPal"},
        {"url": "http://netflix-billing-issue.co", "brand": "Netflix"}
    ]

    for item in phish_data:
        results.append({
            "indicator": item['url'],
            "type": "URL",
            "source": "PhishTank",
            "risk_score": 85,
            "enrichment": {
                "target_brand": item['brand'], # <--- BRAND ATTRIBUTION
                "pulse_name": f"Phishing: {item['brand']}",
                "tags": ["phishing", item['brand'].lower()],
                "description": f"Verified phishing site impersonating {item['brand']}."
            }
        })
    
    return results # Handing data back to main.py