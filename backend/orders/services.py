"""Les règles métier sont ici : les vues ne font que valider et répondre."""
from decimal import Decimal
from bson import ObjectId
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from common.db import database, get_document, transaction
from delivery.services import assign_available_driver

TRANSITIONS = {
    "pending": {"accepted", "cancelled"},
    "accepted": {"preparing", "out_for_delivery", "delivered", "cancelled"},
    "preparing": {"out_for_delivery", "delivered", "cancelled"},
    "out_for_delivery": {"delivered", "cancelled"},
    "delivered": set(), "cancelled": set(),
}

def money(value):
    return str(value.quantize(Decimal("0.01")))


def create_order(data):
    def apply(session):
        get_document("clients", data["client_id"], session)
        items = []
        for item in data["items"]:
            meal = get_document("meals", item["meal_id"], session)
            if not meal["available"] or meal["date"] != timezone.localdate().isoformat():
                raise ValidationError({"items": "Seuls les repas disponibles du jour peuvent être commandés."})
            price = Decimal(meal["price"])
            items.append({"meal_id": item["meal_id"], "name": meal["name"], "quantity": item["quantity"],
                          "unit_price": money(price), "subtotal": money(price * item["quantity"])})
        subtotal = sum((Decimal(item["subtotal"]) for item in items), Decimal("0"))
        fee = Decimal("0") if subtotal >= settings.FREE_DELIVERY_THRESHOLD else settings.DEFAULT_DELIVERY_FEE
        order_id = ObjectId()
        driver = assign_available_driver(order_id, session)
        now = timezone.now()
        order = {"_id": order_id, "client_id": data["client_id"], "items": items,
                 "subtotal": money(subtotal), "delivery_fee": money(fee), "total": money(subtotal + fee),
                 "status": "accepted" if driver else "pending",
                 "delivery_driver_id": str(driver["_id"]) if driver else None,
                 "estimated_delivery_minutes": settings.DEFAULT_DELIVERY_ESTIMATE if driver else None,
                 "created_at": now, "updated_at": now}
        database().orders.insert_one(order, session=session)
        return order
    return transaction(apply)


def update_order_status(pk, target):
    def apply(session):
        order = get_document("orders", pk, session)
        if target == order["status"]:
            return order
        if target not in TRANSITIONS[order["status"]]:
            raise ValidationError({"status": "Transition de statut interdite."})
        changes = {"status": target, "updated_at": timezone.now()}
        if target == "accepted" and not order["delivery_driver_id"]:
            driver = assign_available_driver(order["_id"], session)
            if driver is None:
                raise ValidationError({"status": "Aucun livreur disponible ; la commande reste pending."})
            changes.update(delivery_driver_id=str(driver["_id"]), estimated_delivery_minutes=settings.DEFAULT_DELIVERY_ESTIMATE)
        if target in {"delivered", "cancelled"}:
            if order["delivery_driver_id"]:
                database().delivery_drivers.update_one(
                    {"_id": ObjectId(order["delivery_driver_id"]), "active_order_id": str(order["_id"])},
                    {"$set": {"status": "available", "active_order_id": None, "updated_at": timezone.now()}}, session=session)
            changes["estimated_delivery_minutes"] = 0 if target == "delivered" else None
        database().orders.update_one({"_id": order["_id"]}, {"$set": changes}, session=session)
        order.update(changes)
        return order
    return transaction(apply)


def tracking(order):
    driver = None
    if order["delivery_driver_id"]:
        document = database().delivery_drivers.find_one({"_id": ObjectId(order["delivery_driver_id"])})
        if document:
            driver = {"id": str(document["_id"]), "first_name": document["first_name"],
                      "latitude": document.get("latitude"), "longitude": document.get("longitude")}
    return {"order_id": str(order["_id"]), "status": order["status"], "driver": driver,
            "estimated_delivery_minutes": order["estimated_delivery_minutes"]}
