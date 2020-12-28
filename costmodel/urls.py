from django.urls import path, reverse_lazy
from . import views

app_name='costmodel'
urlpatterns = [
    
    # User Cost Breakdown List URL
    path('my-breakdowns/', views.MyBreakdownList.as_view(), name='my_breakdown_list'),

]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined
