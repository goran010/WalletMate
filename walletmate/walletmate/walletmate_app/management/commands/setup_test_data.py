import random

from django.db import transaction
from django.core.management.base import BaseCommand

from walletmate_app.models import ExpenseCategory, Transaction, User, Budget, UserProfile

from walletmate_app.factory import (
    ExpenseCategoryFactory,
    TransactionFactory,
    UserFactory,
    BudgetFactory,
    UserProfileFactory,
)


NUM_USERS = 5
NUM_CATEGORIES = 10
NUM_TRANSACTIONS = 50
NUM_BUDGETS = 10

class Command(BaseCommand):
    help = "Generates test data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models = [Transaction, ExpenseCategory, Budget, UserProfile, User]
        for m in models:
            m.objects.all().delete()

        self.stdout.write("Creating new data...")

        # Create Users
        users = [UserFactory() for _ in range(NUM_USERS)]

        # Create Expense Categories
        categories = [ExpenseCategoryFactory() for _ in range(NUM_CATEGORIES)]

        # Create Transactions
        for _ in range(NUM_TRANSACTIONS):
            TransactionFactory(
                category=random.choice(categories)
            )

        # Create Budgets
        for _ in range(NUM_BUDGETS):
            BudgetFactory(
                user=random.choice(users),
                category=random.choice(categories),
            )

        # Create User Profiles
        for user in users:
            UserProfileFactory(user=user)

        self.stdout.write(self.style.SUCCESS("Test data generated successfully!"))
