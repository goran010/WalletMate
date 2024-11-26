from django.http import HttpResponse
from django.shortcuts import render
from .models import Transaction

def home(request):
    return HttpResponse("Welcome to WalletMate!")


def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions})
