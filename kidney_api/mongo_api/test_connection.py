from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_DETAILS = "mongodb+srv://hospital_db_user:hospital123@cluster0.8ef3cwc.mongodb.net/?appName=Cluster0"

try:
    print("--- Starting new connection test (Insecure Mode) ---")
    
    # This test skips SSL certificate validation.
    # It's a test to see if a firewall/antivirus is the problem.
    client = MongoClient(
        MONGO_DETAILS,
        server_api=ServerApi('1'),
        tls=True,
        tlsInsecure=True  # <-- THIS IS THE NEW LINE
    )
    
    client.admin.command('ping')
    print("✅✅✅ VICTORY! (Insecure Mode) ✅✅✅")
    print("Pinged your deployment. You successfully connected to MongoDB!")
    print("\nCONCLUSION: Your Antivirus or Firewall is breaking the connection.")
    print("You will need to add this 'tlsInsecure=True' setting to your main.py file.")


except Exception as e:
    print("\n❌❌❌ Test Failed Again ❌❌❌")
    print("Even the insecure connection failed. This is a severe network block.")
    print("Error details:\n")
    print(e)

finally:
    if 'client' in locals():
        client.close()