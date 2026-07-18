from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email="admin@finmark.ai").exists():
            User.objects.create_superuser(
                email="admin@finmark.ai",
                password="Finmark@2026",
                first_name="Admin",
                last_name="Finmark",
            )
            self.stdout.write("Superuser created: admin@finmark.ai")
        else:
            self.stdout.write("Superuser already exists")
