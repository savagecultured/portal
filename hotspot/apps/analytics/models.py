from django.db import models
from django.conf import settings
from django.utils import timezone


class Session(models.Model):
    """Tracks time and bandwidth for one portal session."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sessions'
    )
    token = models.OneToOneField(
        'tokens.Token',
        on_delete=models.SET_NULL,
        null=True,
        related_name='session'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    bytes_rx = models.BigIntegerField(default=0)
    bytes_tx = models.BigIntegerField(default=0)
    ip_address = models.GenericIPAddressField()

    @property
    def duration_seconds(self):
        if self.end_time:
            return (self.end_time - self.start_time).seconds
        from django.utils import timezone
        return (timezone.now() - self.start_time).seconds

    @property
    def total_bytes(self):
        return self.bytes_rx + self.bytes_tx

    def __str__(self):
        return f'Session {self.id} — {self.user.email}'