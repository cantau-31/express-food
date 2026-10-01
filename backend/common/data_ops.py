"""Outils de donnees : sauvegarde, restauration et controle d'integrite des collections MongoDB.

Partie "Data & integration" du projet. Reutilise la couche PyMongo partagee (common.db)
et n'introduit aucun ODM. Les documents sont serialises en JSON etendu MongoDB
(bson.json_util), qui preserve les types ObjectId et datetime lors d'un aller-retour.
"""
from decimal import Decimal, InvalidOperation
from pathlib import Path

from bson import json_util
from django.conf import settings
from django.utils import timezone

from common.db import database, ensure_indexes

# Les quatre collections metier, dans l'ordre de dependance (clients et repas avant commandes).
COLLECTIONS = ("clients", "meals", "delivery_drivers", "orders")


def export_collections(output_path):
    """Ecrit toutes les collections dans un fichier JSON et renvoie le nombre de documents par collection."""
    db = database()
    payload = {
        "database": settings.MONGODB_DATABASE,
        "exported_at": timezone.now().isoformat(),
        "collections": {name: list(db[name].find()) for name in COLLECTIONS},
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json_util.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {name: len(documents) for name, documents in payload["collections"].items()}


def import_collections(input_path, drop=True):
    """Recharge les collections depuis un fichier JSON. Par defaut, remplace les collections existantes."""
    payload = json_util.loads(Path(input_path).read_text(encoding="utf-8"))
    collections = payload.get("collections", {})
    db = database()
    counts = {}
    for name in COLLECTIONS:
        documents = collections.get(name, [])
        if drop:
            db[name].drop()
        if documents:
            db[name].insert_many(documents)
        counts[name] = len(documents)
    ensure_indexes()
    return counts


def _decimal(value):
    return Decimal(str(value))


def check_integrity():
    """Verifie les invariants data et renvoie la liste des anomalies (vide = base coherente).

    Lecture seule : references commandes -> clients/livreurs, arithmetique des montants,
    coherence entre le statut d'un livreur et sa commande active. Ne modifie aucune donnee.
    """
    db = database()
    anomalies = []

    client_ids = {str(doc["_id"]) for doc in db.clients.find({}, {"_id": 1})}
    drivers = {str(doc["_id"]): doc for doc in db.delivery_drivers.find()}
    orders = {str(doc["_id"]): doc for doc in db.orders.find()}

    seen_emails = set()
    for doc in db.clients.find({}, {"email": 1}):
        email = doc.get("email")
        if email in seen_emails:
            anomalies.append(f"client: email en double '{email}'.")
        seen_emails.add(email)

    for meal in db.meals.find():
        if meal.get("type") not in ("dish", "dessert"):
            anomalies.append(f"meal {meal['_id']}: type invalide '{meal.get('type')}'.")
        try:
            if _decimal(meal.get("price")) <= 0:
                anomalies.append(f"meal {meal['_id']}: prix non positif '{meal.get('price')}'.")
        except (InvalidOperation, TypeError):
            anomalies.append(f"meal {meal['_id']}: prix non numerique '{meal.get('price')}'.")

    for oid, order in orders.items():
        if order.get("client_id") not in client_ids:
            anomalies.append(f"order {oid}: client_id introuvable ({order.get('client_id')}).")
        driver_id = order.get("delivery_driver_id")
        if driver_id and driver_id not in drivers:
            anomalies.append(f"order {oid}: delivery_driver_id introuvable ({driver_id}).")
        try:
            subtotal = _decimal(order["subtotal"])
            fee = _decimal(order["delivery_fee"])
            total = _decimal(order["total"])
            if total != subtotal + fee:
                anomalies.append(f"order {oid}: total {total} != subtotal {subtotal} + frais {fee}.")
            items_sum = sum((_decimal(item["subtotal"]) for item in order.get("items", [])), Decimal("0"))
            if items_sum != subtotal:
                anomalies.append(f"order {oid}: somme des lignes {items_sum} != subtotal {subtotal}.")
            for item in order.get("items", []):
                if _decimal(item["unit_price"]) * item["quantity"] != _decimal(item["subtotal"]):
                    anomalies.append(f"order {oid}: ligne '{item.get('name')}' sous-total incoherent.")
        except (InvalidOperation, TypeError, KeyError) as error:
            anomalies.append(f"order {oid}: montants illisibles ({error}).")

    for driver_id, driver in drivers.items():
        active = driver.get("active_order_id")
        if (driver.get("status") == "delivering") != bool(active):
            anomalies.append(f"driver {driver_id}: statut '{driver.get('status')}' incoherent avec active_order_id={active}.")
        if active:
            order = orders.get(str(active))
            if order is None:
                anomalies.append(f"driver {driver_id}: active_order_id {active} introuvable.")
            elif order.get("delivery_driver_id") != driver_id:
                anomalies.append(f"driver {driver_id}: la commande {active} ne le reference pas.")

    return anomalies
