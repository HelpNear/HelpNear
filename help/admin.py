from django.contrib import admin
from .models import HelpRequest, HelpResponse, Opinion, Profile

@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'is_open', 'created_at']
    list_filter = ['is_open', 'category']
    search_fields = ['title', 'description', 'user__username']

@admin.register(HelpResponse)
class HelpResponseAdmin(admin.ModelAdmin):
    list_display = ['request', 'responder', 'rating', 'created_at']
    search_fields = ['request__title', 'responder__username']

@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ['helper', 'author', 'rating', 'created_at']
    search_fields = ['helper__username', 'author__username', 'description']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']
