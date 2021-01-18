from django.urls import path
from breakdowns import views
from breakdowns.views import CostBreakdownList

app_name = 'breakdowns'

urlpatterns = [
    path('index/', CostBreakdownList.as_view(), name='index'),
    #path('index/', views.index, name='index'),
    path('detail/<int:costbreakdown_id>/', views.detail, name="detail"),
    path('dashboard/', views.dashboard, name='dashboard'),
]

