from django.urls import path
from breakdowns import views
from breakdowns.views import CostBreakdownList, CostBreakdownDetail

app_name = 'breakdowns'

urlpatterns = [
    path('index/', CostBreakdownList.as_view(), name='index'),
    path('detail/<int:pk>/', CostBreakdownDetail.as_view(), name="detail"),
    #path('index/', views.index, name='index'),
    #path('detail/<int:costbreakdown_id>/', views.detail, name="detail"),
    path('dashboard/', views.dashboard, name='dashboard'),
]

