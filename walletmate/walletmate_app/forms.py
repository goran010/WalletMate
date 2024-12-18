from django import forms
from .models import Transaction, ExpenseCategory

class TransactionFilterForm(forms.Form):
    transaction_type = forms.ChoiceField(
        choices=[('', 'All'), ('income', 'Income'), ('expense', 'Expense')],
        required=False,
        label="Transaction Type"
    )
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        required=False,
        label="Category"
    )
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Start Date")
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="End Date")
    search = forms.CharField(required=False, label="Search")
