import subprocess
import webbrowser
import os
import re
from flask import Flask, render_template, jsonify, request
# IMPORTANT: Ensure this import matches your actual file structure
from src.database.db_connection import get_database 

app = Flask(__name__)

# Global variable to track the currently running sub-process
current_task_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute/<task>')
def execute_task(task):
    global current_task_process
    target_url = request.args.get('target', 'google.com')
    
    commands = {
        "intel": ["python3", "-m", "src.main"],
        "enforce": ["sudo", "python3", "-m", "src.processors.policy_enforcer"],
        "test": ["sudo", "python3", "-m", "src.tests.pen_test_sim", target_url],
        "auto_test": ["sudo", "python3", "-m", "src.tests.auto_pentest"],
        "rollback": ["bash", "-c", "echo 'yes' | sudo python3 -m src.utils.rollback"]
    }
    
    if task not in commands:
        return jsonify({"output": "Invalid Task Requested", "status": "error"}), 400
    
    try:
        current_task_process = subprocess.Popen(
            commands[task], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = current_task_process.communicate(timeout=300)
        
        status = "open"
        if "100% packet loss" in stdout or "0 received" in stdout:
            status = "blocked"
            
        if current_task_process.returncode == 0:
            return jsonify({"output": stdout, "status": status})
        else:
            return jsonify({"output": f"PROCESS ERROR:\n{stderr or stdout}", "status": "error"})
            
    except subprocess.TimeoutExpired:
        if current_task_process:
            os.system(f"sudo kill -9 {current_task_process.pid}")
            current_task_process = None
        return jsonify({"output": "[!] Phase Timeout: Task exceeded 300 seconds.", "status": "error"})
    except Exception as e:
        return jsonify({"output": f"Backend Exception: {str(e)}", "status": "error"}), 500

@app.route('/execute/unblock')
def unblock_ip():
    target_ip = request.args.get('target')
    if not target_ip:
        return jsonify({"output": "No IP provided.", "status": "error"}), 400
    try:
        cmd = ["sudo", "iptables", "-D", "INPUT", "-s", target_ip, "-j", "DROP"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"output": f"[+] SUCCESS: {target_ip} unblocked.", "status": "open"})
        else:
            return jsonify({"output": f"[-] FAILED: Rule not found for {target_ip}.", "status": "error"})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}", "status": "error"}), 500

@app.route('/execute/view_blocked')
def view_blocked():
    """Queries the Linux kernel and resolves IPs back to their specific Source/URL"""
    try:
        # 1. Fetch live rules from the kernel
        result = subprocess.run(['sudo', 'iptables', '-nL', 'INPUT'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        live_ips = []
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 4 and parts[0] == "DROP":
                ip = parts[3].split('/')[0] # Clean netmasks
                if ip != "0.0.0.0":
                    live_ips.append(ip)

        if not live_ips:
            return jsonify({"items": []})

        # 2. Connect to MongoDB for Intelligence Enrichment
        db = get_database()
        if db is None:
            return jsonify({"items": [{"indicator": ip, "url": "DB Offline", "score": "!"} for ip in live_ips]})

        collection = db["threat_indicators"]
        
        # 3. Retrieve documents for live IPs, sorted by Risk Score
        enriched_list = []
        cursor = collection.find(
            {"indicator": {"$in": live_ips}},
            {"_id": 0, "indicator": 1, "risk_score": 1, "source": 1, "url": 1}
        ).sort("risk_score", -1).limit(50)

        for doc in cursor:
            # PRIORITIZATION LOGIC:
            # 1. Use URL if it's a phishing link (PhishTank)
            # 2. Use Source if it's an IP reputation hit (AbuseIPDB/AlienVault)
            # 3. Default to "Enriched Threat"
            display_info = doc.get("url") or doc.get("source") or "Enriched Threat"
            
            enriched_list.append({
                "indicator": doc.get("indicator"),
                "url": display_info,
                "score": doc.get("risk_score", 0)
            })
            
        # 4. Fallback for any IPs in the kernel not found in the DB
        found_ips = [item['indicator'] for item in enriched_list]
        for ip in live_ips:
            if ip not in found_ips and len(enriched_list) < 50:
                enriched_list.append({
                    "indicator": ip,
                    "url": "Direct Kernel Block",
                    "score": "N/A"
                })

        return jsonify({"items": enriched_list})
    except Exception as e:
        return jsonify({"output": f"Kernel Error: {str(e)}", "status": "error"})
@app.route('/terminate_task', methods=['POST'])
def terminate_task():
    global current_task_process
    if current_task_process and current_task_process.poll() is None:
        try:
            os.system(f"sudo kill -9 {current_task_process.pid}")
            current_task_process = None
            return jsonify({"success": True, "message": "Task terminated safely."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Kill failed: {str(e)}"})
    return jsonify({"success": False, "message": "No active process."})
@app.route('/execute/manual_block')
def manual_block():
    """Manually pushes a specific IP to the iptables DROP list"""
    target_ip = request.args.get('target')
    if not target_ip:
        return jsonify({"output": "No IP provided.", "status": "error"}), 400

    try:
        # Check if already blocked to avoid duplicates
        check = subprocess.run(["sudo", "iptables", "-C", "INPUT", "-s", target_ip, "-j", "DROP"], capture_output=True)
        if check.returncode == 0:
            return jsonify({"output": f"[!] {target_ip} is already blocked.", "status": "blocked"})

        # Apply the DROP rule
        cmd = ["sudo", "iptables", "-A", "INPUT", "-s", target_ip, "-j", "DROP"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({"output": f"[+] MANUAL BLOCK SUCCESS: {target_ip}", "status": "blocked"})
        else:
            return jsonify({"output": f"[-] FAILED: {result.stderr}", "status": "error"})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}", "status": "error"}), 500

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
