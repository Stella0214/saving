from django.urls import path
from . import views

app_name='breakdowns'
urlpatterns = [
    
    # User Cost Breakdown List URL
    path('my-breakdowns/', views.MyBreakdownList.as_view(), name='my_breakdown_list'),

]

