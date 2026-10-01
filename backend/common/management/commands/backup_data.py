"""Sauvegarde les collections MongoDB dans un fichier JSON (partie Data & integration)."""
from django.core.management.base import BaseCommand
from django.utils import timezone

from common.data_ops import export_collections


class Command(BaseCommand):
    help = "Exporte les collections MongoDB vers un fichier JSON de sauvegarde."

    def add_arguments(self, parser):
        parser.add_argument("--output", help="Chemin du fichier de sortie (defaut : backups/express_food_<horodatage>.json).")

    def handle(self, *args, **options):
        output = options.get("output") or f"backups/express_food_{timezone.now():%Y%m%d_%H%M%S}.json"
        counts = export_collections(output)
        detail = ", ".join(f"{name}={count}" for name, count in counts.items())
        self.stdout.write(self.style.SUCCESS(f"Sauvegarde de {sum(counts.values())} documents dans {output} ({detail})."))
