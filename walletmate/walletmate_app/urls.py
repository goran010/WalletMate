from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('transactions/', views.transaction_list, name='transaction_list'),
]