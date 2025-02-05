from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)  # Ensures JSON-friendly output

    class Meta:
        model = Transaction
        fields = '__all__'
