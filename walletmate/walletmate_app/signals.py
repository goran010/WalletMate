from django.db.models.signals import post_migrate
from django.core.management import call_command
from django.dispatch import receiver

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
