import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from walletmate_app.models import *

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class ExpenseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ExpenseCategory

    name = factory.Faker("word")
    description = factory.Faker("sentence", nb_words=30)

class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    category = factory.Iterator(ExpenseCategory.objects.all())
    amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    transaction_type = factory.Iterator(["income", "expense"])
    date = factory.Faker("date")
    description = factory.Faker("sentence", nb_words=30)


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    currency = factory.Faker("currency_code")


class BudgetFactory(DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.Iterator(ExpenseCategory.objects.all())
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    start_date = factory.Faker("date_between", start_date="-1y", end_date="today")
    end_date = factory.Faker("date_between", start_date="today",end_date="+1y")
                            