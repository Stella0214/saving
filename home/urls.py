from django.urls import path
from . import views

app_name='home'
urlpatterns = [
    path('', views.HomeView.as_view()),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
]