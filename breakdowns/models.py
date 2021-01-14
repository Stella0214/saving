from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Unit(models.Model):
    """
    Model representing material measurement units
    Example: Kg, m, litre, m2, m3, ml, quintal etc
    """
    title = models.CharField(max_length=60)

    class Meta:
        ordering = ['title']

    def __str__(self):
        """
        Returns string representation of the Unit model
        """
        return self.title

# costmodel 1st level breakdown
# should cost = material cost + manufacturing cost + overhead cost + special cost + profit cost
class CostBreakdown(models.Model):
    """
    Model representing a cost breakdown
    """

    title = models.CharField(max_length=120, help_text='Costmodel Title') # costmodel title
    part_number = models.CharField(max_length=120, help_text='Part Number') # customer or manufacturer part number
    company = models.CharField(max_length=120, help_text='Company') # company or supplier for the part number
    overhead = models.DecimalField('Overhead (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 10 for 10% Overhead') # will connect to class overhead
    packaging = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    freight = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    customs = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tooling = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    profit = models.DecimalField('Profit (%)',null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 5 for 5% Profit')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'cost breakdown'
        verbose_name_plural = 'cost breakdowns'
        ordering = ['title']
        #???
        permissions = (    
                ('download_cost_breakdown', 'Can download cost breakdown in excel and pdf'),
                ('manage_cost_breakdown', 'Can manage own cost breakdown'),
                ('manage_library', 'Can manage standard cost breakdown library'),
            ) 
    
    def __init__(self, *args, **kwargs):  
        super(CostBreakdown, self).__init__(*args, **kwargs)
        self.mb_list = tuple(MaterialBreakdown.objects.filter(costbreakdown_id=self.pk))
        self.gb_list = tuple(ManufacturingBreakdown.objects.filter(costbreakdown_id=self.pk))
            
    def material_cost(self, *args, **kwargs):
        """
        Returns total material cost
        """
        result = 0
        for mb in self.mb_list:
            result += mb.materialtotal()

        return result

    def manufacturing_cost(self, *args, **kwargs): 
        """
        Returns total manufacturing cost
        """
        result = 0
        for gb in self.gb_list:
            result += gb.manufacturingtotal()

        return result

    def production_cost(self, *args, **kwargs): 
        """
        Returns the production cost of the breakdown
        """
        return self.material_cost() + self.manufacturing_cost()

    def overhead_cost(self, *args, **kwargs):
        """
        Returns the overhead cost
        """
        return round((self.overhead / 100) * self.production_cost(), 2)

    def special_cost(self, *args, **kwargs): 
        """
        Returns the special cost of the breakdown
        """
        return round(self.packaging + self.freight + self.customs + self.tooling, 2)  

    def profit_cost(self, *args, **kwargs):
        """
        Returns the profit
        """
        return round((self.profit / 100) * self.production_cost(), 2)

    def indirect_cost(self, *args, **kwargs):
        """
        Returns the indirect cost (overhead + specail + profit) of the breakdown
        """
        return self.overhead_cost() + self.special_cost() + self.profit_cost()

    def total_cost(self, *args, **kwargs):
        """
        Returns the total cost of the cost breakdown 
        """
        return self.production_cost() + self.indirect_cost()
    #???
    def get_absolute_url(self):
        """
        Returns a particular instance of costbreakdown
        """
        return reverse('breakdowns:my_breakdown_detail', kwargs={'pk': str(self.pk)})

    def __str__(self):
        """
        Returns string repsentation of the CostBreakdown model
        """
        return self.title

class MaterialBreakdown(models.Model):
    """
    Model representing a material breakdown
    """
    costbreakdown = models.ForeignKey(CostBreakdown, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, help_text='Material Title') # material title
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE) 
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    scrap = models.DecimalField('Scrap (%)',null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 1 for 1% Scrap')
    overhead = models.DecimalField('Overhead (%)', null=True, blank=True, max_digits=6, decimal_places=2, help_text='Example: Enter 3 for 3% Overhead')

    class Meta:
       verbose_name = 'material breakdown'
       verbose_name_plural = 'material breakdowns'
       ordering = ['costbreakdown', 'title', '-price'] 

    def material_net_cost(self):
        """
        Returns a single material net cost
        """
        return round(self.quantity * self.price, 2)  
    
    def material_scrap_cost(self):
        """
        Returns a single material scrap cost
        """
        return round(self.material_net_cost / (1 - self.scrap / 100) - self.material_net_cost, 2) 

    def material_overhead_cost(self):
        """
        Returns a single material overhead cost
        """
        return round((self.material_net_cost + self.material_scrap_cost) * self.overhead / 100, 2) 

    def materialtotal(self):
        """
        Returns subtotal of a single material cost
        """
        return round(self.material_net_cost + self.material_scrap_cost + self.material_overhead_cost, 2)

    def get_absolute_url(self):
        """
        Returns a particular instance of materialbreakdown
        """
        return reverse('breakdowns:materialbreakdown_detail', kwargs={'pk': str(self.pk)})

    def __str__(self):
        """
        Returns string repsentation of the MaterialBreakdown model
        """
        return '{} Material Breakdown'.format(self.title)

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
        return round(self.manufacturing_net_cost / (1 - self.scrap / 100) - self.manufacturing_net_cost, 2) 

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


