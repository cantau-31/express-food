"""Un client PyMongo partagé ; aucune connexion réseau à l'import."""
from functools import lru_cache
from bson import ObjectId
from django.conf import settings
from pymongo import MongoClient
from rest_framework.exceptions import NotFound

@lru_cache(maxsize=1)
def mongo_client():
    return MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000, tz_aware=True)

def database():
    return mongo_client()[settings.MONGODB_DATABASE]

def transaction(callback):
    with mongo_client().start_session() as session:
        return session.with_transaction(callback)

def get_document(collection, pk, session=None):
    if not ObjectId.is_valid(pk):
        raise NotFound("Identifiant invalide.")
    document = database()[collection].find_one({"_id": ObjectId(pk)}, session=session)
    if document is None:
        raise NotFound("Ressource introuvable.")
    return document

def ensure_indexes():
    db = database()
    db.clients.create_index("email", unique=True)
    db.meals.create_index([("date", 1), ("available", 1)])
    db.delivery_drivers.create_index("status")
    db.delivery_drivers.create_index("active_order_id")
    db.orders.create_index("client_id")
    db.orders.create_index("status")
    db.orders.create_index("delivery_driver_id")
    db.orders.create_index("created_at")
