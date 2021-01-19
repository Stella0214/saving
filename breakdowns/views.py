
from django.views.decorators.csrf import csrf_exempt
import json
from breakdowns import models

from .models import CostBreakdown
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView  # 导入
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.shortcuts import render, redirect, get_object_or_404


#from django.contrib.auth.decorators import login_required

#@login_required
'''
def index(request):

    breakdowns = models.CostBreakdown.objects.all()

    return render(request, 'breakdowns/index.html', locals())
'''

# All My Cost breakdowns list
class CostBreakdownList(OwnerListView):
    model = CostBreakdown
    context_object_name = 'costbreakdown_list'
    template_name = 'breakdowns/costbreakdown_list.html'

class CostBreakdownDetail(OwnerDetailView):
    model = CostBreakdown
    context_object_name = 'costbreakdown'
    template_name = 'breakdowns/costbreakdown_detail.html'

class CostBreakdownCreate(OwnerCreateView):
    model = CostBreakdown
    fields = ['company', 'country', 'region', 'industry', 'description', 'part_number', 'material_cost', 'manufacturing_cost', 'overhead_cost', 'special_cost', 'profit']

class CostBreakdownUpdate(OwnerUpdateView):
    model = CostBreakdown
    fields = ['company', 'country', 'region', 'industry', 'description', 'part_number', 'material_cost', 'manufacturing_cost', 'overhead_cost', 'special_cost', 'profit']

class CostBreakdownDelete(OwnerDeleteView):
    model = CostBreakdown

'''
    def test_func(self, *args, **kwargs):
        breakdowns = models.CostBreakdown.objects.all()
        return breakdowns

    def get_queryset(self, *args, **kwargs):
        return CostBreakdown.objects.filter(created_by__pk=self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        context = super(MyBreakdownList, self).get_context_data(*args, **kwargs)
        context['page_name'] = 'my cost breakdowns'
        return context


#@login_required
def detail(request, costbreakdown_id):
    breakdown = get_object_or_404(models.CostBreakdown, id=costbreakdown_id)
    return render(request, 'breakdowns/detail.html', locals())
'''

#@login_required
def dashboard(request):
    pass
    return render(request, 'breakdowns/dashboard.html', locals())
