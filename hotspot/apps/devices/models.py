from django.db import models
from django.conf import settings


class Device(models.Model):
    """WiFi device fingerprint bound to a user profile."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices'
    )
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=100, blank=True)
    os_hint = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.mac_address} ({self.device_type or "Unknown"}) — {self.user}'