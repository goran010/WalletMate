from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', views.transaction_list, name='transaction_list'),
]