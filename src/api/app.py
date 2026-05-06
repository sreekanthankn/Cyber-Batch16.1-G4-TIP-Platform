import subprocess
import os
from flask import Flask, render_template, jsonify, request
from src.database.db_connection import get_database

app = Flask(__name__)

current_task_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/indicators', methods=['GET'])
def get_indicators():
    limit = request.args.get('limit', default=50, type=int)
    db = get_database()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    collection = db["threat_indicators"]
    total_count = collection.count_documents({})
    otx_count = collection.count_documents({"source": "AlienVault OTX"})
    abuse_count = collection.count_documents({"source": "AbuseIPDB"})
    phish_count = collection.count_documents({"source": "PhishTank"})
    enriched_count = collection.count_documents({"enrichment": {"$exists": True}})
    high_risk_count = collection.count_documents({"risk_score": {"$gte": 90}})
    summary = {
        "platform_status": "ONLINE",
        "total_indicators": total_count,
        "enriched_indicators": enriched_count,
        "high_risk_count": high_risk_count,
        "health_percentage": round((enriched_count / total_count * 100), 2) if total_count > 0 else 0,
        "source_breakdown": {
            "AlienVault_OTX": otx_count,
            "AbuseIPDB": abuse_count,
            "PhishTank": phish_count
        }
    }
    indicators = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
    return jsonify({
        "dashboard_summary": summary,
        "view_metadata": {"requested_limit": limit, "actual_delivered": len(indicators)},
        "data": indicators
    })

@app.route('/api/v1/search', methods=['GET'])
def search_indicator():
    indicator = request.args.get('indicator')
    if not indicator:
        return jsonify({"error": "Missing 'indicator' parameter"}), 400
    db = get_database()
    result = db["threat_indicators"].find_one({"indicator": indicator}, {"_id": 0})
    if result:
        return jsonify({"status": "found", "data": result})
    return jsonify({"status": "not found", "message": "Indicator not in database"}), 404

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Returns stats for SOC Dashboard - Total Blocked IPs and Threat Origins"""
    db = get_database()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    collection = db["threat_indicators"]
    total = collection.count_documents({})
    high_risk = collection.count_documents({"risk_score": {"$gte": 90}})
    phish = collection.count_documents({"source": "PhishTank"})
    otx = collection.count_documents({"source": "AlienVault OTX"})
    abuse = collection.count_documents({"source": "AbuseIPDB"})
    brands = list(collection.aggregate([
        {"$match": {"enrichment.target_brand": {"$exists": True, "$ne": "Unknown"}}},
        {"$group": {"_id": "$enrichment.target_brand", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]))
    return jsonify({
        "total_indicators": total,
        "high_risk_blocked": high_risk,
        "source_breakdown": {
            "PhishTank": phish,
            "AlienVault_OTX": otx,
            "AbuseIPDB": abuse
        },
        "top_targeted_brands": [{"brand": b["_id"], "count": b["count"]} for b in brands]
    })

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
            commands[task], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
        return jsonify({"output": "[!] Task exceeded 300 seconds.", "status": "error"})
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
    try:
        result = subprocess.run(['sudo', 'iptables', '-nL', 'INPUT'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        live_ips = []
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 4 and parts[0] == "DROP":
                ip = parts[3].split('/')[0]
                if ip != "0.0.0.0":
                    live_ips.append(ip)
        if not live_ips:
            return jsonify({"items": []})
        db = get_database()
        if db is None:
            return jsonify({"items": [{"indicator": ip, "url": "DB Offline", "score": "!"} for ip in live_ips]})
        collection = db["threat_indicators"]
        enriched_list = []
        cursor = collection.find(
            {"indicator": {"$in": live_ips}},
            {"_id": 0, "indicator": 1, "risk_score": 1, "source": 1, "url": 1}
        ).sort("risk_score", -1).limit(50)
        for doc in cursor:
            display_info = doc.get("url") or doc.get("source") or "Enriched Threat"
            enriched_list.append({
                "indicator": doc.get("indicator"),
                "url": display_info,
                "score": doc.get("risk_score", 0)
            })
        found_ips = [item['indicator'] for item in enriched_list]
        for ip in live_ips:
            if ip not in found_ips and len(enriched_list) < 50:
                enriched_list.append({"indicator": ip, "url": "Direct Kernel Block", "score": "N/A"})
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

if __name__ == '__main__':
    print("[*] Cyber-TIP API Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
