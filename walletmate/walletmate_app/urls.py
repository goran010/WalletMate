from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from walletmate_app.views import TransactionViewSet, TransactionUpdateAPIView

# Traditional Django views
urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('transaction-report/', views.transaction_report, name='transaction_report'),
]

# API-specific routes
router = DefaultRouter()
router.register(r'api/transactions', TransactionViewSet, basename='transaction')  # ViewSet handles all CRUD actions

# Add router-generated URLs to urlpatterns
urlpatterns += router.urls

