from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from .forms import TransactionFilterForm
from django.shortcuts import render
from django.http import JsonResponse
from .models import Transaction, ExpenseCategory
from django.template.loader import render_to_string
from django.db.models import Q


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


def transaction_list(request):
    # Get the filter parameters from the request
    transaction_type = request.GET.get('transaction_type', '')
    category_id = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search = request.GET.get('search')

    # Start with all transactions
    transactions = Transaction.objects.all()

    # Apply filters
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if search:
            # You can filter by amount or user (assuming `amount` is a number and `user` is a ForeignKey)
        transactions = transactions.filter(
                Q(description__icontains=search) |
                Q(amount__icontains=search) |
                Q(user__username__icontains=search)  # Assuming you have a user field in the model
            )

    # Get all categories for the filter dropdown
    categories = ExpenseCategory.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the transactions part of the template as HTML
        transactions_html = render_to_string('walletmate_app/transaction_list_partial.html', {'transactions': transactions})
        return JsonResponse({'transactions_html': transactions_html})

    # If not an AJAX request, render the full page
    return render(request, 'walletmate_app/transaction_list.html', {'transactions': transactions, 'categories': categories})


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'walletmate_app/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        # Only show transactions for the logged-in user
        return Transaction.objects.all()



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
