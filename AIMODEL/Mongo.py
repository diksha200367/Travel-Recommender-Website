import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB running locally
client = MongoClient("mongodb://localhost:27017/")

# Access your database
db = client["tourismDB"]  # Your database name
collection = db["destinations"]  # Your collection name

# Load CSV file
csv_file = "DATA_FINAL (version 1).csv"  # Change this to your actual file name
df = pd.read_csv(csv_file)

# Convert DataFrame to JSON (MongoDB stores data in JSON format)
data_json = df.to_dict(orient="records")

# Insert data into MongoDB
collection.insert_many(data_json)

print("✅ CSV data successfully loaded into MongoDB!")

