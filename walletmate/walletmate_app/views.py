from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'walletmate_app/index.html')

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')

    else:
        form = UserCreationForm()

    context = {'form': form}

    return render(request, 'registration/register.html', context)

