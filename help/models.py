from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

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
    detailed_expectation = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    address = models.CharField(max_length=255, default='Unknown address')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_open = models.BooleanField(default=True)
    accepted_response = models.ForeignKey('HelpResponse', null=True, blank=True, on_delete=models.SET_NULL, related_name='accepted_for')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class HelpResponse(models.Model):
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response from {self.responder.username} on {self.request.title}"

# New profile model for phone number
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

User.add_to_class('average_rating', property(lambda u: 
    HelpResponse.objects.filter(responder=u, rating__isnull=False).aggregate(avg=Avg('rating'))['avg'] or 0))
class Opinion(models.Model):
    helper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opinions_received')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opinions_given')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Opinion about {self.helper.username} by {self.author.username}"

    def display_rating(self):
        return self.rating if self.rating > 0 else "No rating"