import requests
import time

API_URL = "http://127.0.0.1:5000/indicators"

def fetch_high_risk_ips():
    try:
        res = requests.get(API_URL)
        data = res.json()

        high_risk_ips = [
            item.get("indicator")
            for item in data
            if item.get("risk_score", 0) >= 90
        ]

        return high_risk_ips

    except Exception as e:
        print(f"[ERROR] API fetch failed: {e}")
        return []


def simulate_attack(ip):
    print(f"[!] Simulating attack from IP: {ip}")

    try:
        requests.get(f"http://{ip}", timeout=2)
        print(f"[?] {ip} responded (NOT BLOCKED)")
        return False
    except:
        print(f"[✓] {ip} blocked or unreachable")
        return True


def run_test():
    print("\n[***] Starting Penetration Test...\n")

    ips = fetch_high_risk_ips()

    if not ips:
        print("[!] No high-risk IPs found")
        return

    print(f"[+] Testing {len(ips[:5])} high-risk IPs...\n")

    blocked = 0

    for ip in ips[:5]:
        if simulate_attack(ip):
            blocked += 1
        time.sleep(1)

    print("\n====== TEST RESULT ======")
    print(f"Total Tested: {len(ips[:5])}")
    print(f"Blocked: {blocked}")
    print(f"Success Rate: {(blocked/len(ips[:5]))*100:.2f}%")
    print("=========================\n")


if __name__ == "__main__":
    run_test()