from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_migrate
from django.core.management import call_command
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_migrate)
def load_fixtures(sender, **kwargs):
    if sender.name == "walletmate_app":
        fixtures = [
            "content_types.json",
            "permissions.json",
            "users.json",
            "groups.json",
            "expense_categories.json",
            "transactions.json",
            "user_profiles.json",
            "budgets.json",
        ]
        for fixture in fixtures:
            call_command("loaddata", f"walletmate_app/fixtures/{fixture}")
