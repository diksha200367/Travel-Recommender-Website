"""from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# ✅ Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["tourismDB"]
    collection = db["destinations"]
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Error connecting to MongoDB:", e)

# ✅ Homepage Route (Fixes 404 for "/")
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Tourism API! Use /get_destinations to fetch data."})

# ✅ Get All Destinations Route
@app.route('/get_destinations', methods=['GET'])
def get_destinations():
    try:
        data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's _id
        if not data:
            return jsonify({"message": "No destinations found"}), 404
        return jsonify({"destinations": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Run Flask Server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True) 
"""
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["tourismDB"]
collection = db["destinations"]

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Tourism API! Use /recommend to fetch recommendations."})

@app.route('/recommend', methods=['POST'])
def recommend_destinations():
    try:
        data = request.get_json()
        season_filter = data.get("season", [])
        activity_filter = data.get("activity", [])

        # Convert to lowercase for case-insensitive search
        season_filter = [s.lower() for s in season_filter]
        activity_filter = [a.lower() for a in activity_filter]

        # Construct MongoDB query
        query = {"$and": []}

        if season_filter:
            query["$and"].append({"Season": {"$in": season_filter}})
        if activity_filter:
            query["$and"].append({"Activities": {"$regex": "|".join(activity_filter), "$options": "i"}})

        # If no filters, return all destinations
        if not query["$and"]:
            query = {}

        results = list(collection.find(query, {"_id": 0}))

        return jsonify({"recommended_spots": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
