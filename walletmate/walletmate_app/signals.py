from django.db.models.signals import post_migrate
from django.core.management import call_command
from django.dispatch import receiver

@receiver(post_migrate)
def load_fixtures(sender, **kwargs):
    if sender.name == "walletmate_app":
        call_command("loaddata", "walletmate_app/fixtures/expensecategory.json")
        call_command("loaddata", "walletmate_app/fixtures/transactions.json")
        call_command("loaddata", "walletmate_app/fixtures/userprofiles.json")
        call_command("loaddata", "walletmate_app/fixtures/budget.json")
        call_command("loaddata", "walletmate_app/fixtures/users.json")
        call_command("loaddata", "walletmate_app/fixtures/groups.json")