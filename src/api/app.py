from flask import Flask, jsonify, request
from src.database.db_connection import get_database

app = Flask(__name__)

@app.route('/api/v1/indicators', methods=['GET'])
def get_indicators():
    """
    Returns a summarized dashboard and a list of threat indicators.
    Allows dynamic scaling via the 'limit' parameter.
    Example: /api/v1/indicators?limit=934
    """
    # 1. Get dynamic limit from URL (Default to 50 for performance)
    limit = request.args.get('limit', default=50, type=int)
    
    db = get_database()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    collection = db["threat_indicators"]
    
    # 2. GENERATE DYNAMIC STATUS SUMMARY (Real-time Analytics)
    total_count = collection.count_documents({})
    otx_count = collection.count_documents({"source": "AlienVault OTX"})
    abuse_count = collection.count_documents({"source": "AbuseIPDB"})
    phish_count = collection.count_documents({"source": "PhishTank"})
    enriched_count = collection.count_documents({"enrichment": {"$exists": True}})
    
    summary = {
        "platform_status": "ONLINE",
        "total_indicators": total_count,
        "enriched_indicators": enriched_count,
        "health_percentage": round((enriched_count / total_count * 100), 2) if total_count > 0 else 0,
        "source_breakdown": {
            "AlienVault_OTX": otx_count,
            "AbuseIPDB": abuse_count,
            "PhishTank": phish_count
        }
    }

    # 3. FETCH THREAT DATA
    # We sort by timestamp descending to show the newest threats first
    indicators = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))

    # 4. RETURN UNIFIED RESPONSE
    return jsonify({
        "dashboard_summary": summary,
        "view_metadata": {
            "requested_limit": limit,
            "actual_delivered": len(indicators)
        },
        "data": indicators
    })

@app.route('/api/v1/search', methods=['GET'])
def search_indicator():
    """Search for a specific IP, Domain, or URL in the database."""
    indicator = request.args.get('indicator')
    if not indicator:
        return jsonify({"error": "Missing 'indicator' parameter"}), 400

    db = get_database()
    result = db["threat_indicators"].find_one({"indicator": indicator}, {"_id": 0})
    
    if result:
        return jsonify({"status": "found", "data": result})
    return jsonify({"status": "not found", "message": "Indicator not in database"}), 404

if __name__ == '__main__':
    # 0.0.0.0 allows access from other devices on the same network
    print("[*] Cyber-TIP API Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
