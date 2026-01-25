from django.urls import path
from . import views
from .views import (dashboard_view, onboard_wallet, onboard_income, onboard_expense)

urlpatterns = [
 path('dashboard/', dashboard_view, name='dashboard'),
 path('onboarding/wallet/', onboard_wallet, name='onboard_wallet'),
 path('onboarding/income/', onboard_income, name='onboard_income'),
 path('onboarding/expense/', onboard_expense, name='onboard_expense'),
 path('transactions/', views.transaction_list, name='transactions'),
 path('transactions/add/', views.transaction_add, name='transaction_add'),
 path('transactions/<int:tx_id>/edit/', views.transaction_edit, name='transaction_edit'),
 path('transactions/<int:tx_id>/delete/', views.transaction_delete, name='transaction_delete'),
 
 # Settings index
 path('settings/', views.settings_home, name='settings_home'),

 # Wallet
 path('settings/wallets/', views.wallet_list, name='wallet_list'),
 path('settings/wallets/add/', views.wallet_add, name='wallet_add'),
 path('settings/wallets/<int:id>/edit/', views.wallet_edit, name='wallet_edit'),
 path('settings/wallets/<int:id>/delete/', views.wallet_delete, name='wallet_delete'),

 # Category
 path('settings/categories/', views.category_list, name='category_list'),
 path('settings/categories/add/', views.category_add, name='category_add'),
 path('settings/categories/<int:id>/edit/', views.category_edit, name='category_edit'),
 path('settings/categories/<int:id>/delete/', views.category_delete, name='category_delete'),
]