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
import openpyxl
from xlrd import open_workbook
from xlwt import Workbook, easyxf, Formula
from xlutils.copy import copy
from .forms import SignupForm, StepOneForm, StepTwoForm, CreateBreakdownForm, ChooseLibraryForm
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

# My Cost Breakdowns Detail
class MyBreakdownDetail(UserPassesTestMixin, generic.DetailView):
    model = CostBreakdown
    template_name = 'breakdowns/my_breakdown_detail.html'
    context_object_name = 'cost_breakdown'
    login_url = 'breakdowns:my_breakdown_list'
    redirect_field_name = None

    def test_func(self, *args, **kwargs):
        cost_breakdown = CostBreakdown.objects.get(pk=self.kwargs['pk'])
        return cost_breakdown.created_by.id == self.request.user.id

    def get(self, *args, **kwargs):
        if self.request.GET.get('excel'):
            # Get context object
            self.object = self.get_object()

            # Get Material and manufacturing list
            material_list = list(MaterialBreakdown.objects.filter(costbreakdown_id=self.object.id).order_by('-rate'))
            manufacturing_list = list(manufacturingBreakdown.objects.filter(costbreakdown_id=self.object.id).order_by('-hourly_rate'))

            row_count = max(len(material_list), len(manufacturing_list))

            # Import Excel Template
            if row_count <= 14:
                excel_template_path = settings.MEDIA_ROOT + 'blank_template_sm_2.xls'
            elif row_count > 14 and row_count <= 18:
                pass
            else:
                pass
            
            rb = open_workbook(excel_template_path, formatting_info=True)
            wb = copy(rb)
            ws = wb.get_sheet(0)
            
            style_default = easyxf('font: name Courier New, height 180;')
            style_default_center_bold = easyxf('font: name Courier New, height 180, bold on; align: horiz center')
            style_left = easyxf('font: name Courier New, height 180; borders: left thin, right thin, top thin, bottom thin; align: horiz left;')
            style_center = easyxf('font: name Courier New, height 180; borders: left thin, right thin, top thin, bottom thin; align: horiz center;')
            style_right = easyxf('font: name Courier New, height 180; borders: left thin, right thin, top thin, bottom thin; align: horiz right;')
            style_left_bold = easyxf('font: name Courier New, height 180; borders: left thin, right thin, top thin, bottom thin; align: horiz left; font: bold on;')
            style_center_bold = easyxf('font: name Courier New, height 180, bold on; borders: left thin, right thin, top thin, bottom thin; align: horiz center;')
            style_right_bold = easyxf('font: name Courier New, height 180, bold on; borders: left thin, right thin, top thin, bottom thin; align: horiz right;')
            style_center_shade = easyxf('font: name Courier New, height 180; borders: left thin, right thin, top thin, bottom thin; align: horiz center; pattern: pattern solid, fore_colour yellow;')
            style_percent = easyxf(num_format_str='0.00%')

            # Add General breakdown data to excel
            ws.write(0, 3, self.object.project.full_title, style_default)
            ws.write(1, 3, self.object.project.client, style_default)
            ws.write(2, 3, self.object.project.consultant, style_default)
            ws.write(3, 3, self.object.project.contractor, style_default)
            ws.write(5, 3, self.object.full_title, style_default)
            ws.write(0, 15, self.object.project.city, style_center_shade)
            # ws.write(1, 15, self.object.created_at, style_center_shade)
            ws.write(39, 2, self.request.user.get_full_name(), style_default)
            ws.write(35, 16, self.object.overhead/100, style_percent)
            ws.write(36, 16, self.object.profit/100, style_percent)
            ws.write(37, 16, self.object.unit.short_title, style_default_center_bold)

            # Add Material Breakdown data to excel
            if len(material_list) > 0:
                mb_row_count = 12 # Material Excel Row Starts at 7 row

                for i, mb in enumerate(material_list, start=1):
                    ws.write(mb_row_count, 0, i, style_center)
                    ws.write(mb_row_count, 1, mb.material.full_title, style_left)
                    ws.write(mb_row_count, 2, mb.unit.short_title, style_center)
                    ws.write(mb_row_count, 3, mb.quantity, style_right)
                    ws.write(mb_row_count, 4, mb.rate, style_right)
                    ws.write(mb_row_count, 5, Formula("D{}*E{}".format(mb_row_count + 1, mb_row_count + 1)), style_right)
                    mb_row_count += 1

                # Material Subtotal
                ws.write(28, 5, Formula("SUM(F13:F26)"), style_right)
                ws.write(32, 5, Formula("F29"), style_right)

            # Add Labour Breakdown data to excel
            if len(labour_list) > 0:
                lb_row_count = 12 # Labour Excel Row Starts at 7 row
                ws.write(31, 11, self.object.output, style_right)

                for i, lb in enumerate(labour_list, start=1):
                    ws.write(lb_row_count, 7, lb.labour.full_title, style_left)
                    ws.write(lb_row_count, 8, lb.number, style_center)
                    ws.write(lb_row_count, 9, lb.uf, style_center)
                    ws.write(lb_row_count, 10, lb.hourly_rate, style_right)
                    ws.write(lb_row_count, 11, Formula("I{}*J{}*K{}".format(lb_row_count + 1, lb_row_count + 1, lb_row_count + 1)), style_right)
                    lb_row_count += 1

                # Labour Subtotal
                ws.write(28, 11, Formula("ROUND(SUM(L13:L26),2)"), style_right)
                ws.write(32, 11, Formula("L29/L32"), style_right)
            else:
                # Labour Subtotal
                ws.write(32, 11, 0.0, style_right)

            # Add Equipement Breakdown data to excel
            if len(equipment_list) > 0:
                eb_row_count = 12 # Equipement Excel Row Starts at 7 row
                ws.write(31, 17, self.object.output, style_right)

                for i, eb in enumerate(equipment_list, start=1):
                    ws.write(eb_row_count, 13, eb.equipment.full_title, style_left)
                    ws.write(eb_row_count, 14, eb.number, style_center)
                    ws.write(eb_row_count, 15, eb.uf, style_center)
                    ws.write(eb_row_count, 16, eb.rental_rate, style_right)
                    ws.write(eb_row_count, 17, Formula("O{}*P{}*Q{}".format(eb_row_count + 1, eb_row_count + 1, eb_row_count + 1)), style_right)
                    eb_row_count += 1

                # Equipment Subtotal
                ws.write(28, 17, Formula("ROUND(SUM(R13:R26),2)"), style_right)
                ws.write(32, 17, Formula("R29/R32"), style_right)
            else:
                # Equipment Subtotal
                ws.write(32, 17, 0.0, style_right)

            # Direct Cost
            ws.write(34, 17, Formula("SUM(F33+L33+R33)"), style_right)

            # Overhead Cost
            ws.write(35, 17, Formula("ROUND(R35*Q36, 2)"), style_right)

            # Profit Cost
            ws.write(36, 17, Formula("ROUND(R35*Q37,2)"), style_right)

            # Total Cost
            ws.write(37, 17, Formula("SUM(R35+R36+R37)"), style_right_bold)

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=cost_breakdown_{}.xls'.format(self.object.id)

            wb.save(response)
            return response
        return super(MyBreakdownDetail, self).get(*args, **kwargs)
    def get_context_data(self, *args, **kwargs):
        context = super(MyBreakdownDetail, self).get_context_data(*args, **kwargs)         
        context['page_name'] = 'my cost breakdowns'
        return context

# Create a cost breakdown from library
def breakdown_create(request):
    if request.method == 'POST':
        pass
    else:
        if request.GET.get('m') == 'library':
            step = int(request.GET.get('step', 1))
            template_name = 'breakdowns/breakdown_create.html'
            context = {}

            if step == 1:
                context['library_list'] = StandardLibrary.objects.all()
                context['form_html'] = 'breakdowns/partials/breakdown_create_step1.html'
            elif step == 2:
                library = int(request.GET.get('library'))
                context['library_breakdown_list'] = LibraryBreakdown.objects.filter(standard_library=library)
                context['form_html'] = 'breakdowns/partials/breakdown_create_step2.html'
            else:
                pass
        else: # Blank
            pass
    return render(request, template_name, context)


# OLD CODE - Create a new cost breakdown - Step 1
@login_required
def step_one(request):
    form_class = StepOneForm
    step_1_template = 'breakdowns/breakdown_form_step_1.html' #???
    step_2_template = 'breakdowns/breakdown_form_step_2.html' #???

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            option = int(form.cleaned_data['options'])
            if option == 0:
                request.session['library_breakdown'] = CostBreakdown.objects.get(pk=form.cleaned_data['breakdown'].id).id
            else:
                request.session['library_breakdown'] = None
            return redirect('breakdowns:breakdown_create_step_2')
    else:
        request.session['library_breakdown'] = None
        form = form_class()

    return render(request, step_1_template, {
            'form': form,
        })

# Create a new cost breakdown - Step 2
@login_required
def step_two(request):
    form_class = StepTwoForm
    template_name = 'breakdowns/breakdown_form_step_2.html' #???
    catagory_list = CostBreakdownCatagory.objects.all()
    #unit_list = Unit.objects.all()
    unit_catagory_list = UnitCatagory.objects.all()
    project_list = Project.objects.filter(created_by = request.user.id)

    if request.session.get('library_breakdown') is not None:
        library_breakdown = CostBreakdown.objects.get(pk=request.session.get('library_breakdown'))
    elif request.GET.get('library_breakdown') is not None:
        library_breakdown = CostBreakdown.objects.get(pk=int(request.GET.get('library_breakdown')))
    else:
        library_breakdown = None

    if request.method == 'POST': 
        form = form_class(request.POST)
        if form.is_valid():
            cb = form.save(commit=False)
            cb.created_by = request.user
            cb.save()
            
            # If cost_breakdown is duplicated from the library
            if library_breakdown is not None:
                mb_list = MaterialBreakdown.objects.filter(costbreakdown = library_breakdown.id)
                lb_list = LabourBreakdown.objects.filter(costbreakdown = library_breakdown.id)
                eb_list = EquipmentBreakdown.objects.filter(costbreakdown = library_breakdown.id)

                for mb in mb_list:
                    mb.costbreakdown = cb
                    mb.pk = None
                    mb.save()

                for lb in lb_list:
                    lb.costbreakdown = cb
                    lb.pk = None
                    lb.save()

                for eb in eb_list:
                    eb.costbreakdown = cb
                    eb.pk = None
                    eb.save()
            # Destroy session data        
            request.session.library_breakdown = None

            # Redirect to newly created cost breakdown
            return redirect(reverse('breakdowns:my_breakdown_detail', kwargs={'pk': cb.id}))           
    else:
        form = form_class()
    return render(request, template_name, {
            'form': form,
            'catagory_list': catagory_list,
            'unit_catagory_list': unit_catagory_list,
            'library_breakdown': library_breakdown,
            'project_list': project_list,
        })

# Update an Existing Breakdown
class BreakdownUpdate(LoginRequiredMixin, UpdateView):
    """
    Update existing cost breakdown
    """
    model = CostBreakdown
    fields = ['activity_catagory', 'project', 'full_title', 'description', 'unit', 'output', 'overhead', 'profit',]
    template_name = 'breakdowns/breakdown_form_update.html'

    def get_success_url(self, *args, **kwargs):
        return reverse('breakdowns:my_breakdown_detail', kwargs={'pk': self.object.id})

    def get_context_data(self, *args, **kwargs):
        context = super(BreakdownUpdate, self).get_context_data(*args, **kwargs)
        context['project_list'] = Project.objects.filter(created_by=self.request.user.id)
        context['catagory_list'] = CostBreakdownCatagory.objects.all()
        context['unit_catagory_list'] = UnitCatagory.objects.all()
        context['page_name'] = 'mybreakdowns'
        return context

# Delete an Existing Breakdown
class BreakdownDelete(LoginRequiredMixin, DeleteView):
    """
    Delete an existing cost breakdown
    """
    model = CostBreakdown
    template_name = 'breakdowns/breakdown_confirm_delete.html'

    def get_success_url(self, *args, **kwargs):
        if self.object.is_library:
            return reverse('breakdowns:cost_breakdown_list')
        return reverse('breakdowns:my_breakdown_list')

# Create a new cost breakdown view
class BreakdownCreate(LoginRequiredMixin, CreateView):
    """
    Create a new cost breakdown with the current user as it's owner
    """
    model = CostBreakdown
    template_name = 'breakdowns/breakdown_form.html' #???
    fields = ['activity_catagory', 'project', 'full_title', 'description', 'unit', 'output', 'overhead', 'profit',]

    def form_valid(self, form, *args, **kwargs):
        form.instance.created_by = self.request.user
        return super(BreakdownCreate, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('breakdowns:my_breakdown_detail', kwargs={'pk': self.object.id})

    def get_context_data(self, *args, **kwargs):
        context = super(BreakdownCreate, self).get_context_data(*args, **kwargs)
        context['project_list'] = Project.objects.filter(created_by=self.request.user.id)
        context['catagory_list'] = CostBreakdownCatagory.objects.all()
        context['unit_list'] = Unit.objects.all()
        context['subpage_name'] = 'My Breakdowns'
        return context