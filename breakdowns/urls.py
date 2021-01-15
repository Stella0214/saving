from django.urls import path
from breakdowns import views

app_name = 'breakdowns'

urlpatterns = [
    #path('index/', views.MyBreakdownList.as_view(), name='index'),
    path('index/', views.index, name='index'),
    path('detail/<int:costbreakdown_id>/', views.detail, name="detail"),
    path('dashboard/', views.dashboard, name='dashboard'),
]

