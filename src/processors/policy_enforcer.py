import subprocess
from src.database.db_connection import get_database

def fetch_high_risk_threats():
    """Queries MongoDB for IPv4 threats with a risk score >= 90."""
    db = get_database()
    if db is None:
        return []
    
    collection = db["threat_indicators"]
    # Only target IPv4 for iptables and ensure enrichment exists for accuracy
    query = {
        "type": "IPv4",
        "risk_score": {"$gte": 90},
        "enrichment": {"$exists": True}
    }
    
    return list(collection.find(query).limit(100))
    

def apply_firewall_policy(threats):
    """Generates and applies iptables DROP rules."""
    print(f"[*] Analyzing {len(threats)} high-risk indicators for enforcement...")
    
    blocked_count = 0
    for threat in threats:
        ip = threat['indicator']
        try:
            # -C checks if the rule already exists to avoid duplicates
            check_cmd = f"sudo iptables -C INPUT -s {ip} -j DROP"
            result = subprocess.run(check_cmd.split(), capture_output=True)
            
            if result.returncode != 0:
                # Rule doesn't exist, so add it
                add_cmd = f"sudo iptables -A INPUT -s {ip} -j DROP"
                subprocess.run(add_cmd.split(), check=True)
                print(f"[+] BLOCKED: {ip} (Source: {threat['source']})")
                blocked_count += 1
        except Exception as e:
            print(f"[-] Failed to block {ip}: {e}")
            
    print(f"\n[SUCCESS] Policy Enforcer active. {blocked_count} new rules applied.")

if __name__ == "__main__":
    active_threats = fetch_high_risk_threats()
    if active_threats:
        apply_firewall_policy(active_threats)
    else:
        print("[!] No high-risk threats found requiring immediate action.")
