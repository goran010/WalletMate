from django.urls import path
from . import views
from walletmate_app.views import  TransactionDetailView

urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
