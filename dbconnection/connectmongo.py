from pymongo import MongoClient

uri="mongodb+srv://hospital_db_user:hospital123@cluster0.8ef3cwc.mongodb.net/?appName=Cluster0&retryWrites=true&w=majority"
client = MongoClient(uri)

db = client["hospitaldb"]  # Create or access your database
collection = db["hospitaldb"]

# Insert a test document
collection.insert_one({"name": "John", "email": "john@example.com"})

print(" Connected and inserted document successfully!")

client.close()