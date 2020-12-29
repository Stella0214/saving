from django.urls import path, re_path
from . import views

app_name='breakdowns'
urlpatterns = [
        
    # User Cost Breakdown List URL
    re_path(r'^my-breakdowns/$', views.MyBreakdownList.as_view(), name='my_breakdown_list'),

]

