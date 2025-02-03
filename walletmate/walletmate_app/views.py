from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Transaction, ExpenseCategory, UserProfile
from .forms import ExpenseForm, TransactionForm
from .serializers import TransactionSerializer
from django.db.models import Sum
from django.utils.timezone import now

# --- Constants ---
HOMEPAGE_TEXT = "Welcome to WalletMate!"

# --- Utility Functions ---
def is_admin(user):
    """Check if a user belongs to the Admin group."""
    return user.groups.filter(name='Admin').exists()

# --- Views ---
@login_required
def index(request):
    """Home page view displaying real financial data."""
    total_income = Transaction.objects.filter(user=request.user, transaction_type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expenses = Transaction.objects.filter(user=request.user, transaction_type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
    total_balance = total_income - total_expenses

    # Fetch recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    context = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_balance": total_balance,
        "recent_transactions": recent_transactions,
        "today": now().strftime("%B %d, %Y"),
    }

    return render(request, 'walletmate_app/index.html', context)


@user_passes_test(is_admin)
def admin_view(request):
    """Admin-only view."""
    return render(request, 'walletmate_app/admin_page.html')


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_group, _ = Group.objects.get_or_create(name='Korisnik')
            user.groups.add(user_group)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Authentication failed. Please try again.")
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """Logout view."""
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    """Display or create the user's profile."""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Automatically create a new profile for the user if it does not exist
        profile = UserProfile.objects.create(user=request.user)
        profile.save()
    
    return render(request, 'walletmate_app/profile.html', {'profile': profile})


@login_required
def transaction_list(request):
    """List transactions with optional filters."""
    transactions = Transaction.objects.filter(user=request.user)
    filters = {
        'transaction_type': request.GET.get('transaction_type'),
        'category_id': request.GET.get('category'),
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
    }
    search = request.GET.get('search')

    # Apply filters
    if filters['transaction_type']:
        transactions = transactions.filter(transaction_type=filters['transaction_type'])
    if filters['category_id']:
        transactions = transactions.filter(category_id=filters['category_id'])
    if filters['start_date']:
        transactions = transactions.filter(date__gte=filters['start_date'])
    if filters['end_date']:
        transactions = transactions.filter(date__lte=filters['end_date'])
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(amount__icontains=search) |
            Q(user__username__icontains=search)
        )

    categories = ExpenseCategory.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        transactions_html = render_to_string('walletmate_app/transaction_list_partial.html', {'transactions': transactions})
        return JsonResponse({'transactions_html': transactions_html})

    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions, 'categories': categories})


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a transaction."""
    model = Transaction
    template_name = 'walletmate_app/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


@login_required
def add_transaction(request):
    """Add a new transaction."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = ExpenseForm()
    return render(request, 'walletmate_app/add_transaction.html', {'form': form})


@login_required
def delete_transaction(request, pk):
    """Delete a transaction."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
    return redirect('transaction_list')


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
    """Generate a transaction report."""
    return render(request, 'walletmate_app/transaction_report.html')


# --- REST Framework Views ---
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
    

