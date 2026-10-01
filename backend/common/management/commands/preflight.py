from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Exécute les vérifications Data / intégration avant une démo ou un déploiement."

    def handle(self, *args, **options):
        steps = (
            ("Connexion MongoDB", "check_mongodb"),
            ("Intégrité des données", "verify_data"),
        )

        for label, command in steps:
            buffer = StringIO()
            try:
                call_command(command, stdout=buffer, stderr=buffer)
            except Exception as exc:
                output = buffer.getvalue().strip()
                if output:
                    self.stderr.write(output)
                raise CommandError(f"Préflight échoué : {label}.") from exc

            output = buffer.getvalue().strip()
            if output:
                self.stdout.write(output)

        self.stdout.write(self.style.SUCCESS("Préflight Data / intégration : OK"))
