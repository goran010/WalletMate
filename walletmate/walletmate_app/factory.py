import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from walletmate_app.models import ExpenseCategory, Transaction, UserProfile, Budget



# Factory for User
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall('set_password', 'password123')  # Default password


# Factory for ExpenseCategory
class ExpenseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ExpenseCategory

    name = factory.Faker("word")
    description = factory.Faker("sentence")


# Factory for Transaction
class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    category = factory.SubFactory(ExpenseCategoryFactory)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    transaction_type = factory.Iterator(["income", "expense"])
    date = factory.Faker("date")
    description = factory.Faker("sentence")


# Factory for UserProfile
class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    currency = factory.Iterator(["EUR", "USD", "GBP"])


# Factory for Budget
class BudgetFactory(DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(ExpenseCategoryFactory)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    start_date = factory.Faker("date_this_year")
    end_date = factory.Faker("date_this_year")

# Creating a User
user = UserFactory()

# Creating an ExpenseCategory
category = ExpenseCategoryFactory()

# Creating a Transaction
transaction = TransactionFactory(category=category)

# Creating a UserProfile
user_profile = UserProfileFactory(user=user)

# Creating a Budget
budget = BudgetFactory(user=user, category=category)