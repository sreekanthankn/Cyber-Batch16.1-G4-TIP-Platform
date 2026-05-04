import subprocess

def flush_all_rules():
    """Clears the INPUT chain and resets policy to ACCEPT."""
    print("[!] EMERGENCY: Flushing all firewall rules...")
    try:
        # Flush the INPUT chain
        subprocess.run(["sudo", "iptables", "-F", "INPUT"], check=True)
        # Ensure default policy is set to ACCEPT so you don't lock yourself out
        subprocess.run(["sudo", "iptables", "-P", "INPUT", "ACCEPT"], check=True)
        print("[SUCCESS] Firewall rules cleared. Connectivity restored.")
    except Exception as e:
        print(f"[-] Rollback failed: {e}")

if __name__ == "__main__":
    confirm = input("Are you sure you want to flush all rules? (y/n): ")
    if confirm.lower() == 'y':
        flush_all_rules()
