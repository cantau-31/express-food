"""Données fictives ; relancer la commande ne réinitialise pas les livreurs occupés."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from common.db import database, ensure_indexes

class Command(BaseCommand):
    help = "Ajoute deux clients, le menu du jour et trois livreurs (sans doublons)."

    def handle(self, *args, **options):
        ensure_indexes()
        db = database()
        now = timezone.now()
        for first, email in (("Julien", "julien@example.com"), ("Emma", "emma@example.com")):
            db.clients.update_one({"email": email}, {"$setOnInsert": {
                "first_name": first, "last_name": "Demo", "email": email,
                "phone": "0600000000", "address": "10 rue de la Démo, Toulouse", "created_at": now}}, upsert=True)
        for name, price, kind in (("Poulet et riz", "12.99", "dish"), ("Curry de légumes", "11.99", "dish"),
                                  ("Mousse au chocolat", "4.50", "dessert"), ("Salade de fruits", "3.99", "dessert")):
            day = timezone.localdate().isoformat()
            db.meals.update_one({"name": name, "date": day}, {"$setOnInsert": {
                "name": name, "description": "Menu de démonstration", "price": price,
                "type": kind, "date": day, "image_url": "", "available": True, "created_at": now}}, upsert=True)
        for first, status, phone in (("Lucas", "available", "0600000001"), ("Thomas", "available", "0600000002"), ("Alex", "offline", "0600000003")):
            db.delivery_drivers.update_one({"first_name": first, "phone": phone}, {"$setOnInsert": {
                "first_name": first, "last_name": "Demo", "phone": phone, "status": status,
                "latitude": None, "longitude": None, "active_order_id": None,
                "created_at": now, "updated_at": now}}, upsert=True)
        self.stdout.write(self.style.SUCCESS("Données de démonstration ajoutées."))
