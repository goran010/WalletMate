from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.conf import settings
import requests
from decimal import Decimal
from datetime import datetime

# Django Class-Based Views (CBV)
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Django Rest Framework (DRF)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

# Local imports
from .models import Transaction, ExpenseCategory, UserProfile
from .forms import ExpenseForm, TransactionForm
from .serializers import TransactionSerializer


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


# Transactions Views
@login_required
def transaction_list(request):
    """Lists transactions with optional filters."""
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply filters if provided
    filters = {
        'transaction_type': request.GET.get('transaction_type'),
        'category_id': request.GET.get('category'),
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
    }
    search = request.GET.get('search')

    if filters['transaction_type']:
        transactions = transactions.filter(transaction_type=filters['transaction_type'])
    if filters['category_id']:
        transactions = transactions.filter(category_id=filters['category_id'])
    if filters['start_date']:
        transactions = transactions.filter(date__gte=filters['start_date'])
    if filters['end_date']:
        transactions = transactions.filter(date__lte=filters['end_date'])
    if search:
        transactions = transactions.filter(Q(description__icontains=search) | Q(amount__icontains=search))

    categories = ExpenseCategory.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        transactions_html = render_to_string('walletmate_app/transaction_list_partial.html', {'transactions': transactions})
        return JsonResponse({'transactions_html': transactions_html})

    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions, 'categories': categories})


@login_required
def add_transaction(request):
    """Adds a new transaction both locally and via API request."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            token = request.user.auth_token.key  # Ensure the user has a valid API token

            data = {
                "amount": float(form.cleaned_data["amount"]),  # Convert Decimal to float
                "description": form.cleaned_data["description"],
                "transaction_type": form.cleaned_data["transaction_type"],
                "category": form.cleaned_data["category"].id,
                "date": form.cleaned_data["date"].strftime('%Y-%m-%d'),  # Convert date to string format
            }

            api_url = f"{settings.BASE_API_URL}/api/transactions/"
            headers = {"Authorization": f"Token {token}"}

            # Send transaction to API
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                # Save to local database only if API request is successful
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                return redirect("transaction_list")
            else:
                form.add_error(None, "Error saving transaction via API.")

    else:
        form = ExpenseForm()

    return render(request, "walletmate_app/add_transaction.html", {"form": form})


@login_required
def delete_transaction(request, pk):
    """Deletes a transaction."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
    return redirect('transaction_list')


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single transaction."""
    model = Transaction
    template_name = 'walletmate_app/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Update a transaction."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'walletmate_app/transaction_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Transaction, pk=self.kwargs['pk'], user=self.request.user)

    def form_valid(self, form):
        form.save()
        return redirect('transaction_list')


@login_required
def transaction_report(request):
    """Generates a transaction report."""
    return render(request, 'walletmate_app/transaction_report.html')


# API Views for Transactions
class TransactionList(APIView):
    """API view for listing and creating transactions."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(ModelViewSet):
    """API ViewSet for CRUD operations on transactions."""
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
