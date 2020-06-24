from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('logout', views.LogoutView.as_view(), name='logout'),

]
