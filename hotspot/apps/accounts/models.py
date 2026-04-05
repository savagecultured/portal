from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


# Zimbabwe phone number validator: +2637xxxxxxxx (12 digits total)
phone_regex = RegexValidator(
    regex=r'^\+2637\d{8}$',
    message="Phone number must be in the format +2637xxxxxxxx (e.g., +263771234567)."
)


class WebmartUser(AbstractUser):
    """Extended user model for Webmart portal."""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13, validators=[phone_regex], blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def available_tokens(self):
        return self.token_set.filter(used=False, expired=False).count()

    def __str__(self):
        return f"{self.email} ({self.username})"