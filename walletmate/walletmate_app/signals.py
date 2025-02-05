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
        call_command("loaddata", "walletmate_app/fixtures/groups.json")  # Groups first
        call_command("loaddata", "walletmate_app/fixtures/users.json")  # Users before profiles
        call_command("loaddata", "walletmate_app/fixtures/userprofiles.json")
        call_command("loaddata", "walletmate_app/fixtures/expensecategory.json")
        
        # Only load budget if it exists
        import os
        if os.path.exists("walletmate_app/fixtures/budget.json"):
            call_command("loaddata", "walletmate_app/fixtures/budget.json")
        
        call_command("loaddata", "walletmate_app/fixtures/transactions.json")
