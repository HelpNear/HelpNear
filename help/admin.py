from django.contrib import admin
from .models import HelpRequest, HelpResponse

admin.site.register(HelpRequest)
admin.site.register(HelpResponse)
