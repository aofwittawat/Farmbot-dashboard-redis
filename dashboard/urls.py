from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('receive-account-data/', views.receive_account_data, name='receive_account_data'),
    path('get_dashboard_data/', views.get_dashboard_data, name='get_dashboard_data'),
    path('add-account/', views.add_account, name='add_account'),
    path('delete-one-account/', views.delete_one_account, name='delete_one_account'),
    path('delete-all-accounts/', views.delete_all_accounts, name='delete_all_accounts'),
]