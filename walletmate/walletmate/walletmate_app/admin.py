from django.contrib import admin
from .models import ExpenseCategory, Transaction, UserProfile, Budget

admin.site.register(ExpenseCategory)
admin.site.register(Transaction)
admin.site.register(UserProfile)
admin.site.register(Budget)


