from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from walletmate_app.views import TransactionViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from .views import TransactionUpdateView
from django.contrib.auth import views as auth_views

# Traditional Django views
urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register, name='register'),
    #path('logout/', views.logout_view, name='logout'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('transaction-report/', views.transaction_report, name='transaction_report'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),

]

# API-specific routes
router = DefaultRouter()

router.register(r'api/transactions', TransactionViewSet, basename='transaction')

# Add router-generated URLs to urlpatterns
urlpatterns += router.urls

urlpatterns += [
    path('api/token/', ObtainAuthToken.as_view(), name='api_token_auth'),
]

