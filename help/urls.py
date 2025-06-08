from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_request, name='create_request'),
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('request/<int:request_id>/edit/', views.edit_request, name='edit_request'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('my-accepted/', views.my_accepted_requests, name='my_accepted_requests'),
    path('request/<int:request_id>/accept/<int:response_id>/', views.accept_response, name='accept_response'),
    path('rate/<int:response_id>/', views.rate_helper, name='rate_helper'),
    path('map/', views.map_view, name='map_view'),
    path('profile/', views.profile_view, name='profile'),
    path('opinion/give/<int:helper_id>/', views.give_opinion, name='give_opinion'),
    path('opinions/<int:helper_id>/', views.helper_opinions, name='helper_opinions'),
    path('helpers/filter/', views.filter_helpers, name='filter_helpers'),
    path('helpers/top/', views.top_helpers, name='top_helpers'),
    path('helpers/top/', views.top_helpers, name='top_helpers'),
    path('helpers/filter/', views.filter_helpers, name='filter_helpers'),
    path('my-opinions/', views.my_opinions, name='my_opinions'),
]
