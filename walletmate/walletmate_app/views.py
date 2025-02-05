from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.conf import settings
import requests

# Django Class-Based Views (CBV)
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Local imports
from .models import Transaction, ExpenseCategory, UserProfile
from .forms import ExpenseForm, TransactionForm

# Utility Functions
def is_admin(user):
    """Check if a user belongs to the Admin group."""
    return user.groups.filter(name='Admin').exists()

# Authentication Views
def register(request):
    """Handles user registration and assigns them to a default group."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_group, _ = Group.objects.get_or_create(name='Korisnik')
            user.groups.add(user_group)
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Authentication failed. Please try again.")
    else:
        form = UserCreationForm()
    return render(request, 'login/register.html', {'form': form})


def logout_view(request):
    """Logs the user out and redirects to the home page."""
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    """Displays or creates the user's profile."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'walletmate_app/profile.html', {'profile': profile})


# Home Page
@login_required
def index(request):
    """Displays a summary of user finances on the home page."""
    total_income = Transaction.objects.filter(user=request.user, transaction_type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expenses = Transaction.objects.filter(user=request.user, transaction_type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
    total_balance = total_income - total_expenses

    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    context = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_balance": total_balance,
        "recent_transactions": recent_transactions,
        "today": now().strftime("%B %d, %Y"),
    }
    return render(request, 'walletmate_app/index.html', context)


# Transactions Views
@login_required
def transaction_list(request):
    """Lists transactions with optional filters."""
    transactions = Transaction.objects.filter(user=request.user)
    categories = ExpenseCategory.objects.all()
    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions, 'categories': categories})


@login_required
def add_transaction(request):
    """Adds a new transaction both locally and via API request."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect("transaction_list")
    else:
        form = ExpenseForm()
    return render(request, "walletmate_app/add_transaction.html", {"form": form})


@login_required
def delete_transaction(request, pk):
    """Deletes a transaction locally and via API request."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    api_url = f"{settings.BASE_API_URL}/api/transactions/{pk}/"
    headers = {"Authorization": f"Token {request.user.auth_token.key}"}
    
    response = requests.delete(api_url, headers=headers)
    if response.status_code == 204:
        transaction.delete()
        return redirect('transaction_list')
    else:
        return JsonResponse({"error": "Failed to delete transaction via API."}, status=400)


# Class-Based Views
class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single transaction."""
    model = Transaction
    template_name = 'walletmate_app/transaction_detail.html'
    context_object_name = 'transaction'


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Update a transaction locally and via API request."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'walletmate_app/transaction_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Transaction, pk=self.kwargs['pk'], user=self.request.user)

    def form_valid(self, form):
        transaction = form.save(commit=False)
        api_url = f"{settings.BASE_API_URL}/api/transactions/{transaction.pk}/"
        headers = {"Authorization": f"Token {self.request.user.auth_token.key}"}
        data = {
            "amount": float(transaction.amount),
            "description": transaction.description,
            "transaction_type": transaction.transaction_type,
            "category": transaction.category.id,
            "date": transaction.date.strftime('%Y-%m-%d')
        }
        
        response = requests.put(api_url, json=data, headers=headers)
        if response.status_code == 200:
            transaction.save()
            return redirect('transaction_list')
        else:
            form.add_error(None, "Failed to update transaction via API.")
            return self.form_invalid(form)
