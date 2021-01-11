from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.shortcuts import redirect

# Create your views here.

class HomeView(View):
    def get(self, request):
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        context = {
            'installed': settings.INSTALLED_APPS,
            'islocal': islocal
        }
        return render(request, 'home/main.html', context)

def login(request):
    pass
    return render(request, 'home/login.html')

def register(request):
    pass
    return render(request, 'home/register.html')

def logout(request):
    pass
    return redirect("/home/")