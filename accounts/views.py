from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('dashboard')  # dashboard nanti kita setup

    return render(request, 'accounts/register.html')


def login_view(request):
 if request.method == 'POST':
  username = request.POST['username']
  password = request.POST['password']
  
  user = authenticate(username=username, password=password)
  if user:
   login(request, user)
   return redirect('dashboard')
  else:
   return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
 return render(request, 'accounts/login.html')


def logout_view(request):
 logout(request)
 return redirect('login')