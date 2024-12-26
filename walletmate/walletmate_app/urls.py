from django.urls import path
from . import views
from walletmate_app.views import  TransactionDetailView
from walletmate_app.views import TransactionDetailView, TransactionUpdateView  # Import the correct view class


urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('profile/', views.profile_view, name='profile'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/<int:pk>/update/', TransactionUpdateView.as_view(), name='transaction_update'),  # Corrected view reference
    path('transaction-report/', views.transaction_report, name='transaction_report'),
]
