from django.db import models
from django.contrib.auth.models import User

class HelpRequest(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food Delivery'),
        ('medicine', 'Buy Medicine'),
        ('house', 'House Help'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class HelpResponse(models.Model):
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
