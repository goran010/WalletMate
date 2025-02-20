from django import forms
from .models import Transaction

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'amount', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 bg-white text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 bg-white text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full p-3 border border-gray-300 bg-white text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 bg-white text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 bg-white text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
                'rows': 3
            }),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'amount', 'category', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full p-3 border border-gray-300 bg-white text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
                'style': 'border-width: 1px;',
                'placeholder': field.label 
            })
