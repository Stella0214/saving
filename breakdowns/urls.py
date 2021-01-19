from django.urls import path, reverse_lazy
from . import views
from breakdowns.views import CostBreakdownList, CostBreakdownDetail, CostBreakdownCreate, CostBreakdownUpdate, CostBreakdownDelete

app_name = 'breakdowns'

urlpatterns = [
    path('', views.CostBreakdownList.as_view(),name='all'),
    path('breakdown/<int:pk>/', views.CostBreakdownDetail.as_view(), name="costbreakdown_detail"),
    path('breakdown/create',
        views.CostBreakdownCreate.as_view(success_url=reverse_lazy('breakdowns:all')), name='costbreakdown_create'),
    path('breakdown/<int:pk>/update',
        views.CostBreakdownUpdate.as_view(success_url=reverse_lazy('breakdowns:all')), name='costbreakdown_update'),
    path('breakdown/<int:pk>/delete',
        views.CostBreakdownDelete.as_view(success_url=reverse_lazy('breakdowns:all')), name='costbreakdown_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

