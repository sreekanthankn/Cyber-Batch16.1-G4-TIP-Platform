# rollback.py
# Week 4 - Firewall Rollback & Flush Logic
# Role: Safety & Integrity Engineer
# Contributor: Amaan Roshan
# Purpose: Emergency Kill Switch to restore network connectivity
#          if the policy enforcer accidentally blocks legitimate services.

import subprocess
import sys
from datetime import datetime

def flush_iptables():
    """
    Flushes all iptables rules and restores default ACCEPT policies.
    This is the emergency kill switch for the platform.
    """
    print("=" * 60)
    print("  CYBER-TIP PLATFORM: FIREWALL ROLLBACK MODULE")
    print("  WARNING: This will flush ALL active firewall rules!")
    print("=" * 60)

    # Confirm before flushing
    confirm = input("\n[!] Are you sure you want to flush all iptables rules? (yes/no): ")
    if confirm.lower() != "yes":
        print("[*] Rollback cancelled. No changes made.")
        return False

    print(f"\n[*] Initiating rollback at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    commands = [
        # Flush all rules in INPUT, OUTPUT, FORWARD chains
        ["iptables", "-F"],
        # Delete all user-defined chains
        ["iptables", "-X"],
        # Zero all packet and byte counters
        ["iptables", "-Z"],
        # Restore default ACCEPT policies
        ["iptables", "-P", "INPUT", "ACCEPT"],
        ["iptables", "-P", "OUTPUT", "ACCEPT"],
        ["iptables", "-P", "FORWARD", "ACCEPT"],
    ]

    descriptions = [
        "Flushing all iptables rules...",
        "Deleting user-defined chains...",
        "Zeroing packet counters...",
        "Restoring INPUT policy to ACCEPT...",
        "Restoring OUTPUT policy to ACCEPT...",
        "Restoring FORWARD policy to ACCEPT...",
    ]

    for cmd, desc in zip(commands, descriptions):
        print(f"[*] {desc}")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"[+] Done.")
        except subprocess.CalledProcessError as e:
            print(f"[-] Failed: {e}")
            return False
        except FileNotFoundError:
            print(f"[-] iptables not found. Are you running on Linux with root?")
            return False

    print("\n[SUCCESS] Firewall rollback complete!")
    print("[*] All rules flushed. Default ACCEPT policies restored.")
    print("[*] Network connectivity has been fully restored.")
    print("=" * 60)
    return True

def show_current_rules():
    """Display current iptables rules before rollback."""
    print("\n[*] Current iptables rules:")
    print("-" * 40)
    try:
        result = subprocess.run(
            ["iptables", "-L", "-n", "--line-numbers"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"[-] Could not retrieve rules: {e}")

if __name__ == "__main__":
    print("\n[*] Checking current firewall state...")
    show_current_rules()
    flush_iptables()
