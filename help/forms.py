from django import forms
from .models import HelpRequest, HelpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['title', 'description', 'category', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class HelpResponseForm(forms.ModelForm):
    class Meta:
        model = HelpResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']