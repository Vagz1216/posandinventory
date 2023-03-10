from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
# Create your views here.

def login_view(request):
    if request.method =='POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('select_store')
            elif user.groups.filter(name='Cashiers').exists():
                return redirect('index')
            elif user.groups.filter(name='Store Managers').exists():
                return redirect('index')
            else:
                # Redirect to some default view for other user groups
                return redirect('login_view')
        else:
            messages.success(request, ("Invalid credentials! Please enter correct password/email"))
            return redirect('login_view')

    return render(request, 'authenticate/login.html')

def logout_view(request):
    logout(request)
    print(request.session.get('store_id'))
    messages.success(request, ("You Were Logged Out!"))
    return redirect('login_view')

def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, 'An email has been sent with instructions to reset your password.')
            return redirect('login_view')
    else:
        form = PasswordResetForm()
    return render(request, 'authenticate/forgot_pass.html', {'form': form})
