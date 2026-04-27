from flask import Flask, jsonify, request
from src.database.db_connection import get_database

app = Flask(__name__)

@app.route('/api/v1/indicators', methods=['GET'])
def get_indicators():
    db = get_database()
    collection = db["threat_indicators"]
    
    # Check for limit parameter (default 50)
    limit = int(request.args.get('limit', 50))
    
    # Calculate health metrics for the dashboard_summary
    total_count = collection.count_documents({})
    enriched_count = collection.count_documents({"enrichment": {"$exists": True}})
    health = round((enriched_count / total_count * 100), 2) if total_count > 0 else 0
    
    # Fetch data
    cursor = collection.find({}, {"_id": 0}).limit(limit)
    data = list(cursor)
    
    return jsonify({
        "dashboard_summary": {
            "enriched_indicators": enriched_count,
            "health_percentage": health,
            "platform_status": "ONLINE"
        },
        "data": data,
        "view_metadata": {
            "actual_delivered": len(data),
            "requested_limit": limit
        }
    })

if __name__ == "__main__":
    app.run(port=5000)