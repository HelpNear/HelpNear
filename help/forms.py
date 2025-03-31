from django import forms
from .models import HelpRequest, HelpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # ← не вистачало!

class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['title', 'description', 'category', 'location', 'email', 'phone']

class HelpResponseForm(forms.ModelForm):
    class Meta:
        model = HelpResponse
        fields = ['message']

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
