from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomRegisterForm(UserCreationForm):
    # We removed the email field entirely
    
    class Meta:
        model = User
        # We only list 'username' here. 
        # UserCreationForm automatically adds the two password fields.
        fields = ["username"]