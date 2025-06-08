from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django import forms
from django.db.models import Avg
from .models import HelpRequest, HelpResponse, Opinion

import json


from .forms import HelpRequestForm, HelpResponseForm, RegisterForm, OpinionForm

# --- Form ---
# class OpinionForm(forms.ModelForm):
#     class Meta:
#         model = Opinion
#         fields = ['rating', 'description']
#         widgets = {
#             'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }


# --- Opinion Views ---
@login_required
def give_opinion(request, helper_id):
    helper = get_object_or_404(User, id=helper_id)
    existing = Opinion.objects.filter(author=request.user, helper=helper).exists()
    if existing:
        return render(request, 'help/give_opinion.html', {
            'form': None,
            'helper': helper,
            'error': "You have already left an opinion for this helper."
        })

    if request.method == 'POST':
        form = OpinionForm(request.POST)
        if form.is_valid():
            opinion = form.save(commit=False)
            opinion.author = request.user
            opinion.helper = helper
            opinion.save()
            return redirect('helper_opinions', helper_id=helper.id)
    else:
        form = OpinionForm()

    return render(request, 'help/give_opinion.html', {'form': form, 'helper': helper})


def helper_opinions(request, helper_id):
    helper = get_object_or_404(User, id=helper_id)
    opinions = Opinion.objects.filter(helper=helper).order_by('-created_at')
    return render(request, 'help/helper_opinions.html', {
        'helper': helper,
        'opinions': opinions
    })


@login_required
def my_opinions(request):
    opinions = Opinion.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'help/my_opinions.html', {'opinions': opinions})


# --- Helper filters ---
def filter_helpers(request):
    min_rating = request.GET.get('min_rating', 1)
    try:
        min_rating = float(min_rating)
    except ValueError:
        min_rating = 1

    helpers = (
        User.objects
        .annotate(avg_rating=Avg('opinions_received__rating'))
        .filter(avg_rating__gte=min_rating)
    )

    return render(request, 'help/filter_helpers.html', {
        'helpers': helpers,
        'min_rating': int(min_rating)
    })


def top_helpers(request):
    helpers = (
        User.objects
        .annotate(avg_rating=Avg('opinions_received__rating'))
        .filter(avg_rating__isnull=False)
        .order_by('-avg_rating')[:10]
    )

    return render(request, 'help/top_helpers.html', {
        'helpers': helpers
    })
# --- Help System ---
def home(request):
    category = request.GET.get('category')
    if category:
        help_requests = HelpRequest.objects.filter(category__icontains=category, is_open=True).order_by('-created_at')
    else:
        help_requests = HelpRequest.objects.filter(is_open=True).order_by('-created_at')
    return render(request, 'help/home.html', {
        'help_requests': help_requests,
        'selected_category': category,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })


@login_required
def create_request(request):
    if request.method == 'POST':
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            help_request = form.save(commit=False)
            help_request.user = request.user
            help_request.save()
            return redirect('home')
    else:
        form = HelpRequestForm()
    return render(request, 'help/create_request.html', {'form': form, 'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY})


@login_required
def edit_request(request, request_id):
    help_request = get_object_or_404(HelpRequest, pk=request_id, user=request.user)
    if request.method == 'POST':
        form = HelpRequestForm(request.POST, instance=help_request)
        if form.is_valid():
            form.save()
            return redirect('request_detail', request_id=request_id)
    else:
        form = HelpRequestForm(instance=help_request)
    return render(request, 'help/edit_request.html', {
        'form': form,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'help_request': help_request
    })


@login_required
def request_detail(request, request_id):
    help_request = get_object_or_404(HelpRequest, pk=request_id)
    responses = help_request.responses.all()
    show_form = request.user.is_authenticated and help_request.is_open and help_request.user != request.user

    if request.method == 'POST' and show_form:
        form = HelpResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.request = help_request
            response.responder = request.user
            response.save()
            return redirect('request_detail', request_id=request_id)
    else:
        form = HelpResponseForm() if show_form else None

    return render(request, 'help/request_detail.html', {
        'help_request': help_request,
        'form': form,
        'responses': responses,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })


@login_required
def accept_response(request, request_id, response_id):
    help_request = get_object_or_404(HelpRequest, pk=request_id, user=request.user)
    response = get_object_or_404(HelpResponse, pk=response_id, request=help_request)
    help_request.accepted_response = response
    help_request.is_open = False
    help_request.save()
    return redirect('request_detail', request_id=request_id)


@login_required
def rate_helper(request, response_id):
    response = get_object_or_404(HelpResponse, pk=response_id, request__user=request.user)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        response.rating = rating
        response.save()
        return redirect('home')
    return render(request, 'help/rate_helper.html', {'response': response})


# --- Auth ---
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'help/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            username = username_or_email

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()
    return render(request, 'help/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def my_requests(request):
    help_requests = HelpRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'help/my_requests.html', {'help_requests': help_requests})


@login_required
def my_accepted_requests(request):
    responses = HelpResponse.objects.filter(
        responder=request.user,
        request__accepted_response__responder=request.user
    ).select_related('request')

    if request.method == 'POST':
        response_id = request.POST.get('response_id')
        feedback = request.POST.get('feedback')
        response = get_object_or_404(HelpResponse, pk=response_id, responder=request.user)
        response.feedback = feedback
        response.save()
        return redirect('my_accepted_requests')

    return render(request, 'help/my_accepted_requests.html', {
        'responses': responses
    })


from .models import Opinion  # переконайся, що є

@login_required
def profile_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        request.user.email = email
        request.user.profile.phone = phone
        request.user.save()
        request.user.profile.save()
        from django.contrib import messages
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    # ⬅️ Додай це
    opinions_received = Opinion.objects.filter(helper=request.user).order_by('-created_at')

    return render(request, 'help/profile.html', {
        'user': request.user,
        'opinions_received': opinions_received,  # ⬅️ Додай
    })


# --- Map ---
def map_view(request):
    help_requests = HelpRequest.objects.filter(is_open=True)
    help_requests_json = json.dumps([
        {
            'id': r.id,
            'title': r.title,
            'latitude': r.latitude,
            'longitude': r.longitude
        } for r in help_requests if r.latitude and r.longitude
    ])
    return render(request, 'help/map_view.html', {
        'help_requests_json': help_requests_json,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })
