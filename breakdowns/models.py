from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

# total_cost = material_cost + manufacturing_cost + overhead_cost + special_cost + profit
class CostBreakdown(models.Model):
    """
    provide total cost
    """
    
    company = models.CharField(max_length=64, help_text='公司') 
    country = models.CharField(max_length=64, help_text='国家') 
    region = models.CharField(max_length=64, help_text='地区') 
    industry = models.CharField(max_length=64, help_text='行业') 
    description = models.CharField(max_length=64, unique=True, help_text='名称') # 不可重复
    part_number = models.CharField(max_length=120, help_text='型号') 
    
    # material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    manufacturing_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # overhead_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # special_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    profit_rate = models.DecimalField('Profit_Rate (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 5 for 5% Profit_Rate')
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '总成本明细'
        verbose_name_plural = '总成本明细'
        ordering = ['company']
    
    def __init__(self, *args, **kwargs):  
        super(CostBreakdown, self).__init__(*args, **kwargs)
        # self.material_list = tuple(MaterialBreakdown.objects.filter(costbreakdown_id=self.pk))
        self.material_list = MaterialBreakdown.objects.filter(costbreakdown_id=self.pk)
        self.overhead_list = OverheadBreakdown.objects.filter(costbreakdown_id=self.pk)
        self.special_list = SpecialBreakdown.objects.filter(costbreakdown_id=self.pk)
    
    def total_cost(self, *args, **kwargs):
        """
        Returns the total cost 
        """
        return round(self.material_cost() + self.manufacturing_cost + self.overhead_cost() + self.special_cost() + self.profit(), 2)
    
    def material_cost(self, *args, **kwargs):
        """
        Returns material total cost
        """
        result = 0
        for material in self.material_list:
            result += material.material_subtotal_cost()
        return result
    
    def overhead_cost(self, *args, **kwargs):
        """
        Returns overhead cost
        """
        return round(self.development_overhead_cost() + self.sales_overhead_cost() + self.administration_overhead_cost() + self.logistics_overhead_cost(), 2)
    
    def development_overhead_cost(self, *args, **kwargs):
        """
        Returns development overhead cost of overhead cost
        """
        result = 0
        for overhead in self.overhead_list:
            result += overhead.development_overhead_rate
        return round((self.material_cost() + self.manufacturing_cost) * result / 100, 2) 

    def sales_overhead_cost(self, *args, **kwargs):
        """
        Returns sales overhead cost of overhead cost
        """
        result = 0
        for overhead in self.overhead_list:
            result += overhead.sales_overhead_rate
        return round((self.material_cost() + self.manufacturing_cost) * result / 100, 2) 
    
    def administration_overhead_cost(self, *args, **kwargs):
        """
        Returns administration overhead cost of overhead cost
        """
        result = 0
        for overhead in self.overhead_list:
            result += overhead.administration_overhead_rate
        return round((self.material_cost() + self.manufacturing_cost) * result / 100, 2) 
    
    def logistics_overhead_cost(self, *args, **kwargs):
        """
        Returns logistics overhead cost of overhead cost
        """
        result = 0
        for overhead in self.overhead_list:
            result += overhead.logistics_overhead_rate
        return round((self.material_cost() + self.manufacturing_cost) * result / 100, 2) 

    def special_cost(self, *args, **kwargs):
        """
        Returns special cost of total cost
        """
        result = 0
        for special in self.special_list:
            result += special.special_total_cost()
        return result
    
    def profit(self, *args, **kwargs):
        """
        Returns profit of total cost
        """
        return round((self.material_cost() + self.manufacturing_cost + self.overhead_cost() + self.special_cost())*self.profit_rate / 100, 2)

    def get_absolute_url(self):
        """
        Returns a particular instance of costbreakdown
        """
        return reverse('breakdowns:costbreakdown_detail', kwargs={'pk': self.pk})    
    
    def __str__(self):
        """
        Returns string repsentation of the CostBreakdown
        """
        return self.description

# material_cost = ∑(bom_cost + loss_cost + material_overhead_cost + indirect_cost)
class MaterialBreakdown(models.Model):
    """
    Model representing a material breakdown
    """
    costbreakdown = models.ForeignKey(CostBreakdown, on_delete=models.CASCADE)

    description = models.CharField(max_length=64, unique=True, help_text='物料名称') # 不可重复
    part_number = models.CharField(max_length=120, unique=True, help_text='物料型号') # 不可重复
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    usage = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    indirect_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    loss_rate = models.DecimalField('Loss_Rate (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 1 for 1% Loss_Rate')
    material_overhead_rate = models.DecimalField('Material_Overhead_Rate (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 3 for 3% Material_Overhead_Rate')

    class Meta:
       verbose_name = '物料明细'
       verbose_name_plural = '物料明细'
       ordering = ['costbreakdown', 'description', '-price'] 

    def bom_cost(self):
        """
        Returns a single material net cost
        """
        return round(self.price * self.usage, 2)  
    
    def loss_cost(self):
        """
        Returns a single material loss cost
        """
        return round(self.bom_cost() * self.loss_rate / 100, 2) 

    def material_overhead_cost(self):
        """
        Returns a single material overhead cost
        """
        return round((self.bom_cost() + self.loss_cost()) * self.material_overhead_rate / 100, 2) 

    def material_subtotal_cost(self):
        """
        Returns subtotal of a single material cost
        """
        return round(self.bom_cost() + self.loss_cost() + self.material_overhead_cost() + self.indirect_cost, 2)

    def __str__(self):
        """
        Returns string repsentation of the MaterialBreakdown model
        """
        return '{} 物料明细'.format(self.description)

# overhead_cost = development_cost + sales_cost + administration_cost + logistics_cost
class OverheadBreakdown(models.Model):
    """
    Model representing a overhead breakdown
    """
    costbreakdown = models.ForeignKey(CostBreakdown, on_delete=models.CASCADE)

    development_overhead_rate = models.DecimalField('Development_Overhead_Rate (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 3 for 3% Development_Overhead_Rate')
    sales_overhead_rate = models.DecimalField('Sales_Overhead_Rate (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 3 for 3% Sales_Overhead_Rate')
    administration_overhead_rate = models.DecimalField('Administration_Overhead_Rate (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 3 for 3% Administration_Overhead_Rate')
    logistics_overhead_rate = models.DecimalField('Logistics_Overhead_Rate (%)',null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 3 for 3% Logistics_Overhead_Rate')
    
    class Meta:
       verbose_name = '管理成本明细'
       verbose_name_plural = '管理成本明细'
       ordering = ['costbreakdown'] 
    
'''
    def __str__(self):
        """
        Returns string repsentation of the MaterialBreakdown model
        """
        return 
'''

class SpecialBreakdown(models.Model):
    """
    Model representing a special cost breakdown
    """
    costbreakdown = models.ForeignKey(CostBreakdown, on_delete=models.CASCADE)
    
    packaging_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    freight_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    duty_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    tooling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tooling_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    manufacturing_parts = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    
    class Meta:
       verbose_name = '其它成本明细'
       verbose_name_plural = '其它成本明细'
       ordering = ['costbreakdown'] 

    def tooling_cost(self):
        """
        Returns a tooling cost
        """
        return round(self.tooling_price * self.tooling_quantity / self.manufacturing_parts, 2)  

    def special_total_cost(self):
        """
        Returns total of special cost
        """
        return round(self.packaging_cost + self.freight_cost + self.duty_cost + self.tooling_cost(), 2)
'''
class ManufacturingBreakdown(models.Model):
    """
    Model representing a manufacturing breakdown
    """
    costbreakdown = models.ForeignKey(CostBreakdown, on_delete=models.CASCADE)
    process_step = models.CharField(max_length=120, help_text='Manufacturing Process Step') 
    labor_quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    labor_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    machine_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text='Machine hourly rate')
    cycle_time = models.DecimalField(max_digits=6, decimal_places=2, help_text='Number of minutes of cycle time')
    parts = models.IntegerField(default=1) # parts per hour
    scrap = models.DecimalField('Scrap (%)',null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 1 for 1% Scrap')
    overhead = models.DecimalField('Overhead (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 30 for 30% Overhead')
    setup = models.DecimalField(max_digits=8, decimal_places=2, default=0.00) # setup cost

    class Meta:
       verbose_name = 'manufacturing breakdown'
       verbose_name_plural = 'manufacturing breakdowns'
       ordering = ['costbreakdown', 'process_step'] 

    def labor_net_cost(self):
        """
        Returns a single labor net cost
        """
        return round((self.labor_quantity * self.labor_rate) * self.cycle_time / self.parts / 60, 2)  

    def machine_net_cost(self):
        """
        Returns a single machine net cost
        """
        return round(self.machine_rate * self.cycle_time / self.parts / 60, 2)   

    def manufacturing_net_cost(self):
        """
        Returns a single manufacturing net cost
        """
        return round(self.labor_net_cost + self.machine_net_cost, 2)   

    def manufacturing_scrap_cost(self):
        """
        Returns a single manufacturing scrap cost
        """
        return round(self.manufacturing_net_cost * self.scrap / 100, 2) 

    def manufacturing_overhead_cost(self):
        """
        Returns a single manufacturing overhead cost
        """
        return round((self.manufacturing_net_cost + self.manufacturing_scrap_cost + self.setup) * self.overhead / 100, 2) 

    def manufacturingtotal(self):
        """ 
        Return manufacturing cost total
        """

        return round(self.manufacturing_net_cost + self.manufacturing_scrap_cost + self.setup + self.manufacturing_overhead_cost, 2)

    def get_absolute_url(self):
        """
        Returns a particular instance of manufacturingbreakdown
        """
        return reverse('breakdowns:manufacturingbreakdown_detail', kwargs={'pk': str(self.pk)})

    def __str__(self):
        """
        Returns string repsentation of the manufacturingbreakdown model
        """
        return '{} Manufacturing Breakdown'.format(self.process_step)
'''

