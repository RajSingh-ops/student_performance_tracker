from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import CustomRegisterForm

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import CustomRegisterForm
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now login.")
            return redirect("login")
    else:
        form = CustomRegisterForm()

    return render(request, "register.html", {"form": form})


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

