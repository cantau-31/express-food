"""Restaure les collections MongoDB depuis un fichier JSON (partie Data & integration)."""
from django.core.management.base import BaseCommand, CommandError

from common.data_ops import import_collections


class Command(BaseCommand):
    help = "Recharge les collections MongoDB depuis un fichier JSON. Par defaut, remplace les donnees existantes."

    def add_arguments(self, parser):
        parser.add_argument("--input", required=True, help="Chemin du fichier JSON a restaurer.")
        parser.add_argument("--keep", action="store_true", help="Inserer sans vider d'abord les collections.")

    def handle(self, *args, **options):
        try:
            counts = import_collections(options["input"], drop=not options["keep"])
        except FileNotFoundError:
            raise CommandError(f"Fichier introuvable : {options['input']}")
        detail = ", ".join(f"{name}={count}" for name, count in counts.items())
        mode = "ajout" if options["keep"] else "remplacement"
        self.stdout.write(self.style.SUCCESS(f"Restauration ({mode}) de {sum(counts.values())} documents ({detail})."))
