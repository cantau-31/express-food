from django.core.management.base import BaseCommand
from common.db import ensure_indexes

class Command(BaseCommand):
    help = "Crée les index MongoDB (à exécuter avant le premier lancement)."
    def handle(self, *args, **options):
        ensure_indexes()
        self.stdout.write(self.style.SUCCESS("Index créés."))
