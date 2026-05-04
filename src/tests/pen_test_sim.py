import sys
import socket
import subprocess

def resolve_target(target):
    """Converts a URL/Domain to an IP address."""
    try:
        # If it's already an IP, this returns it. If it's a URL, it resolves it.
        return socket.gethostbyname(target)
    except Exception:
        return None

def run_test(target):
    print(f"[*] Starting diagnostic for: {target}")
    
    ip = resolve_target(target)
    if not ip:
        print(f"[!] Error: Could not resolve {target}")
        return

    print(f"[*] Resolved IP: {ip}")
    
    # -c 1: Send 1 packet
    # -W 1: Wait only 1 second (essential for the GUI to feel fast)
    cmd = ["ping", "-c", "1", "-W", "1", ip]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the raw output so app.py can read it
    print(result.stdout)
    
    if result.returncode == 0:
        print(f"\n[+] SUCCESS: {target} is REACHABLE.")
    else:
        print(f"\n[-] BLOCKED: {target} is NOT reachable (100% packet loss).")

if __name__ == "__main__":
    # Check if the dashboard sent a target URL/IP as an argument
    if len(sys.argv) > 1:
        user_target = sys.argv[1]
    else:
        user_target = "google.com" # Default fallback
        
    run_test(user_target)
