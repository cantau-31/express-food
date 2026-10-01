"""Controle d'integrite des donnees MongoDB (partie Data & integration)."""
from django.core.management.base import BaseCommand, CommandError

from common.data_ops import check_integrity


class Command(BaseCommand):
    help = "Verifie les invariants data (references, montants, coherence livreur/commande)."

    def handle(self, *args, **options):
        anomalies = check_integrity()
        for anomaly in anomalies:
            self.stdout.write(f"- {anomaly}")
        if anomalies:
            raise CommandError(f"{len(anomalies)} anomalie(s) detectee(s).")
        self.stdout.write(self.style.SUCCESS("Aucune anomalie : les donnees sont coherentes."))
