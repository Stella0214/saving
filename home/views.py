from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.shortcuts import redirect
from . import models

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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        message = '请检查填写的内容！'
        if username.strip() and password:
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = models.User.objects.get(name=username) #???
            except :
                message = '用户不存在！'
                return render(request, 'home/login.html', {'message': message})

            if user.password == password:
                print(username, password)
                return redirect('/')
            else:
                message = '密码不正确！'
                return render(request, 'home/login.html', {'message': message})
        else:
            return render(request, 'home/login.html', {'message': message})
    return render(request, 'home/login.html')

def register(request):
    pass
    return render(request, 'home/register.html')

def logout(request):
    pass
    return redirect("/home/")