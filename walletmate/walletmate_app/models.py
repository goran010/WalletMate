from django.db import models
from django.contrib.auth.models import User


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_display = self.user.username if self.user else "No User"
        return f"{self.transaction_type.capitalize()} - {self.amount} ({self.category.name}, {user_display})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, default='EUR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Removed null=True, blank=True
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Budget amount
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_display = self.user.username if self.user else "No User"
        return f"Budget for {self.category.name} ({user_display}): {self.amount}"
