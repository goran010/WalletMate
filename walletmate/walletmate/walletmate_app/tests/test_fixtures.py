from django.test import TestCase
from walletmate_app.models import ExpenseCategory, Transaction, UserProfile, Budget
from django.contrib.auth.models import User, Group
import json

#check if fixture data is correctly loaded into the database
class FixtureTestCase(TestCase):
    fixtures = [
        'users.json',
        'groups.json',
        'expense_categories.json',
        'transactions.json',
        'user_profiles.json',
        'budgets.json',
    ]

    def get_fixture_count(self, fixture_file):
        with open(f'walletmate_app/fixtures/{fixture_file}', 'r', encoding='utf-8') as f:
            return len(json.load(f))

    def test_fixtures_loaded(self):
        expected_user_count = self.get_fixture_count('users.json')
        expected_group_count = self.get_fixture_count('groups.json')
        expected_expense_category_count = self.get_fixture_count('expense_categories.json')
        expected_transaction_count = self.get_fixture_count('transactions.json')
        expected_user_profile_count = self.get_fixture_count('user_profiles.json')
        expected_budget_count = self.get_fixture_count('budgets.json')

        self.assertEqual(User.objects.count(), expected_user_count)
        self.assertEqual(Group.objects.count(), expected_group_count)
        self.assertEqual(ExpenseCategory.objects.count(), expected_expense_category_count)
        self.assertEqual(Transaction.objects.count(), expected_transaction_count)
        self.assertEqual(UserProfile.objects.count(), expected_user_profile_count)
        self.assertEqual(Budget.objects.count(), expected_budget_count)
