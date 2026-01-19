from pymongo import MongoClient
import certifi

client = MongoClient(
    "mongodb+srv://photo_admin:Qwerty%28789%29@cluster001.sczag4j.mongodb.net/photo_matching?retryWrites=true&w=majority",
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000
)

print(client.admin.command("ping"))
