from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
import json
from breakdowns import models
from django.shortcuts import get_object_or_404

def index(request):

    breakdowns = models.CostBreakdown.objects.all()
    return render(request, 'breakdowns/index.html', locals())


def dashboard(request):
    pass
    return render(request, 'breakdowns/dashboard.html', locals())


def detail(request, costbreakdown_id):
    """
    以显示服务器类型资产详细为例，安全设备、存储设备、网络设备等参照此例。
    :param request:
    :param asset_id:
    :return:
    """
    breakdown = get_object_or_404(models.CostBreakdown, id=costbreakdown_id)
    return render(request, 'breakdowns/detail.html', locals())
