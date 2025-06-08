from django import forms
from .models import HelpRequest, HelpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = [
            'title', 'description', 'detailed_expectation', 'category',
            'address', 'latitude', 'longitude', 'email', 'phone'
        ]
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class HelpResponseForm(forms.ModelForm):
    class Meta:
        model = HelpResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        from .models import Profile  
        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already in use.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.phone = self.cleaned_data['phone']
            user.profile.save()
        return user
from .models import Opinion

class OpinionForm(forms.ModelForm):
    class Meta:
        model = Opinion
        fields = ['rating', 'description']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment...'}),
        }
