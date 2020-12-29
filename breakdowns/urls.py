from django.urls import path, re_path
from . import views

app_name='breakdowns'
urlpatterns = [
        
    # User Cost Breakdown List URL
    re_path(r'^my-breakdowns/$', views.MyBreakdownList.as_view(), name='my_breakdown_list'),

    # User Cost Breakdown Detail URL
    re_path(r'^my-breakdown/(?P<pk>[0-9]+)/$', views.MyBreakdownDetail.as_view(), name='my_breakdown_detail'),

    # User Cost Breakdown Create step 1 URL
    re_path(r'^my-breakdown/create/$', views.breakdown_create, name='breakdown_create'),

    # User Cost Breakdown Create step 2 URL
    re_path(r'^cost-breakdown/create/step-2$', views.step_two, name='breakdown_create_step_2'),

    # Update cost breakdown
    re_path(r'my-breakdown/update/(?P<pk>[0-9]+)/$', views.BreakdownUpdate.as_view(), name="breakdown_update"),

    # Delete cost breakdown
    re_path(r'my-breakdown/delete/(?P<pk>[0-9]+)/$', views.BreakdownDelete.as_view(), name="breakdown_delete"),

]

