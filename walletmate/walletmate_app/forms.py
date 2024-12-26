from django import forms
from .models import Transaction

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'amount', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        
        }
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'transaction_type', 'description', 'date']
