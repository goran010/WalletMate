from django.test import TestCase
from walletmate_app.models import *
from django.contrib.auth.models import User
from datetime import date

#Check if the transaction model correctly saves data and returns the expected string representation
class TestTransactionModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.category = ExpenseCategory.objects.create(name="Groceries")
        self.transaction = Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=100.50,
            transaction_type="expense",
            date=date(2023, 2, 1),
            description="Weekly grocery shopping"
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.user, self.user)
        self.assertEqual(self.transaction.category, self.category)
        self.assertEqual(self.transaction.amount, 100.50)
        self.assertEqual(self.transaction.transaction_type, "expense")
        self.assertEqual(self.transaction.date, date(2023, 2, 1))
        self.assertEqual(self.transaction.description, "Weekly grocery shopping")

    def test_transaction_str_representation(self):
        expected_str = f"{self.transaction.transaction_type.capitalize()} - {self.transaction.amount} ({self.transaction.category.name}, {self.transaction.user.username})"
        self.assertEqual(str(self.transaction), expected_str)