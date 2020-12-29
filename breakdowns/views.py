from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404, HttpResponse
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.core import serializers
from datetime import date
from .models import Unit, CostBreakdown, MaterialBreakdown, ManufacturingBreakdown

# All My Cost breakdowns list
class MyBreakdownList(LoginRequiredMixin, generic.ListView):
    model = CostBreakdown
    template_name = 'breakdowns/my_breakdown_list.html'
    context_object_name = 'cost_breakdown_list'
    login_url = 'breakdowns:my_breakdown_list'
    redirect_field_name = None

    def test_func(self, *args, **kwargs):
        cost_breakdown = CostBreakdown.objects.get(pk=self.kwargs['pk']) #???
        return cost_breakdown.created_by.id == self.request.user.id

    def get_queryset(self, *args, **kwargs):
        return CostBreakdown.objects.filter(created_by__pk=self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        context = super(MyBreakdownList, self).get_context_data(*args, **kwargs)
        context['page_name'] = 'my cost breakdowns'
        return context
