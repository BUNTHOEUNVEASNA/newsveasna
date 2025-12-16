from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class EmailVerificationToken(models.Model):
    """
    Stores a unique token used to verify a user's email address upon registration.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Token expires after 48 hours."""
        expiration_time = self.created_at + timezone.timedelta(hours=48)
        return timezone.now() > expiration_time

    def __str__(self):
        return f"Token for {self.user.username}"


class EmailDigestPreference(models.Model):
    """
    Stores user preferences for the scheduled news email digest (Step C: Settings).
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly',),
        ('monthly', 'Monthly'),
        ('none', 'None (Disabled)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    frequency = models.CharField(
        max_length=10, 
        choices=FREQUENCY_CHOICES, 
        default='daily',
        help_text="How often the user wants to receive the news digest."
    )
    categories = models.JSONField(
        default=list, 
        blank=True,
        help_text="A list of preferred news categories (e.g., ['tech', 'sports'])."
    )
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
    


