from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test


homepage_text = "Promijeni!"


def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def index(request):
    global homepage_text

    if request.method == "POST" and request.user.groups.filter(name='Admin').exists():
        new_text = request.POST.get("homepage_text")
        if new_text.strip():
            homepage_text = new_text
        return redirect('index')

    context = {
        'homepage_text': homepage_text,
        'is_admin': request.user.groups.filter(name='Admin').exists(),
    }
    return render(request, 'walletmate_app/index.html', context)

@user_passes_test(is_admin)
def admin_view(request):
    return render(request, 'admin_page.html')


@login_required
def transaction_list(request):
    if request.user.groups.filter(name='Admin').exists():
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user_group, created = Group.objects.get_or_create(name='Korisnik')
            user.groups.add(user_group)

            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('index')

    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')
