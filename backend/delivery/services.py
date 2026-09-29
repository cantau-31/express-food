"""L'affectation et la commande partagent la même transaction Atlas."""
from django.utils import timezone
from pymongo import ReturnDocument
from rest_framework.exceptions import ValidationError
from common.db import database, get_document, transaction


def assign_available_driver(order_id, session):
    return database().delivery_drivers.find_one_and_update(
        {"status": "available", "active_order_id": None},
        {"$set": {"status": "delivering", "active_order_id": str(order_id), "updated_at": timezone.now()}},
        sort=[("_id", 1)], return_document=ReturnDocument.AFTER, session=session,
    )


def update_driver(pk, values):
    def apply(session):
        driver = get_document("delivery_drivers", pk, session)
        status = values.get("status", driver["status"])
        if driver.get("active_order_id") and status != "delivering":
            raise ValidationError("Terminez ou annulez la commande avant de libérer ce livreur.")
        if not driver.get("active_order_id") and status == "delivering":
            raise ValidationError("Le statut delivering nécessite une commande affectée.")
        changes = {**values, "updated_at": timezone.now()}
        database().delivery_drivers.update_one({"_id": driver["_id"]}, {"$set": changes}, session=session)
        driver.update(changes)
        return driver
    return transaction(apply)
