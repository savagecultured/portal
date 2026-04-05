from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


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
            delta = self.end_time - self.start_time
            return int(delta.total_seconds())
        return int((timezone.now() - self.start_time).total_seconds())

    @property
    def duration_formatted(self):
        seconds = self.duration_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f'{hours}h {minutes}m'
        return f'{minutes}m'

    @property
    def total_bytes(self):
        return self.bytes_rx + self.bytes_tx

    @property
    def bandwidth_formatted(self):
        bytes_total = self.total_bytes
        if bytes_total >= 1024**3:
            return f'{bytes_total / (1024**3):.2f} GB'
        elif bytes_total >= 1024**2:
            return f'{bytes_total / (1024**2):.2f} MB'
        elif bytes_total >= 1024:
            return f'{bytes_total / 1024:.2f} KB'
        return f'{bytes_total} B'

    @property
    def is_active(self):
        return self.end_time is None

    def __str__(self):
        return f'Session {self.id} — {self.user.email}'

    class Meta:
        ordering = ['-start_time']