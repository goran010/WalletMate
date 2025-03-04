from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.conf import settings
import requests
import json
from django.db.models import Sum
from .models import Transaction

# Django Class-Based Views (CBV)
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Local imports
from .models import Transaction, ExpenseCategory, UserProfile
from .forms import ExpenseForm, TransactionForm


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
    return render(request, 'registration/register.html', {'form': form})


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


@login_required
def report(request):
    """Generates a transaction report showing percentage distribution by category."""
    
    # Aggregate total income and expenses for each category
    category_totals = (
        Transaction.objects
        .values("category__name", "transaction_type")
        .annotate(total_amount=Sum("amount"))
    )

    # Calculate total income and total expenses separately
    total_income = sum(t["total_amount"] for t in category_totals if t["transaction_type"] == "income")
    total_expense = sum(t["total_amount"] for t in category_totals if t["transaction_type"] == "expense")

    # Prepare percentage data for chart
    income_data = {}
    expense_data = {}

    for t in category_totals:
        category_name = t["category__name"]
        if t["transaction_type"] == "income":
            income_data[category_name] = float(t["total_amount"] / total_income * 100) if total_income else 0
        elif t["transaction_type"] == "expense":
            expense_data[category_name] = float(t["total_amount"] / total_expense * 100) if total_expense else 0

    # Format data for Chart.js
    chart_data = {
        "income_labels": list(income_data.keys()),
        "income_percentages": list(income_data.values()),
        "expense_labels": list(expense_data.keys()),
        "expense_percentages": list(expense_data.values()),
    }

    return render(request, "walletmate_app/report.html", {"chart_data": json.dumps(chart_data)})


# Transactions Views
@login_required
def transaction_list(request):
    """Lists transactions with optional filters."""
    transactions = Transaction.objects.filter(user=request.user)
    categories = ExpenseCategory.objects.all()

    # Apply filters based on request GET parameters
    transaction_type = request.GET.get('transaction_type', '')
    category_id = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    # Check if the request is an AJAX call
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        transactions_html = render_to_string('walletmate_app/transaction_list_partial.html', {'transactions': transactions}, request)
        return JsonResponse({'transactions_html': transactions_html})

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


def is_admin(user):
    """Provjera je li korisnik superuser ili pripada grupi 'administracija'."""
    return user.is_superuser or user.groups.filter(name='administracija').exists()

@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    search_query = request.GET.get('search', '')
    users = User.objects.all()

    if search_query:
        users = users.filter(username__icontains=search_query)
        
    users_with_admin_status = sorted(
        [{'user': user, 'is_admin': is_admin(user)} for user in users],
        key=lambda x: not x['is_admin']
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
        return render(request, 'walletmate_app/user_list_partial.html', {'users': users_with_admin_status})

    return render(request, 'walletmate_app/user_list.html', {'users': users_with_admin_status})