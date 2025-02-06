from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import ObtainAuthToken

from . import views
from .api_views import TransactionViewSet
from .views import TransactionDetailView, TransactionUpdateView

# API Router
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    # Home & User-related Views
    path('', views.index, name='index'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register, name='register'),
    path('users/', views.user_list_view, name='user_list'),

    # Authentication (Using Django's built-in views)
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    # Transactions Views
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('report/', views.report, name='report'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),

    # Class-Based Views for Transactions
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view(), name='transaction_update'),

    # API Routes
    path('api/', include(router.urls)),
]
