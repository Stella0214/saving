from django.contrib import admin
from costmodel.models import Unit, CostBreakdown, MaterialBreakdown, ManufacturingBreakdown

# Register your models here.

admin.site.register(Unit)
admin.site.register(CostBreakdown)
admin.site.register(MaterialBreakdown)
admin.site.register(ManufacturingBreakdown)