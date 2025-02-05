from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import ObtainAuthToken

from . import views
from .api_views import TransactionViewSet
from .views import (
    TransactionUpdateView, 
    TransactionDetailView
)

# Traditional Django views
urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register, name='register'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('transaction-report/', views.transaction_report, name='transaction_report'),

]

# API-specific routes
router = DefaultRouter()
router.register(r'api/transactions', TransactionViewSet, basename='transaction')

# Add router-generated URLs to urlpatterns
urlpatterns += router.urls

# API Authentication route
urlpatterns += [
    path('api/token/', ObtainAuthToken.as_view(), name='api_token_auth'),
]