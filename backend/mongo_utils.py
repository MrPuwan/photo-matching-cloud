from pymongo import MongoClient

MONGO_URI = "mongodb+srv://photo_admin:Qwerty(789)@cluster001.sczag4j.mongodb.net/?appName=Cluster001"

client = MongoClient(MONGO_URI)

db = client["photo_matching_db"]

clients_col = db["clients"]
matches_col = db["matches"]

print("✅ MongoDB connected successfully")
