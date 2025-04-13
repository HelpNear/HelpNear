from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .models import HelpRequest, HelpResponse
from .forms import HelpRequestForm, HelpResponseForm, RegisterForm
from django.conf import settings

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

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'help/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
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
