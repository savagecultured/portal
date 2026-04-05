import uuid
import subprocess
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Token(models.Model):
    """A single access token granting TOKEN_DURATION_HOURS of portal access."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    source = models.CharField(max_length=30, choices=[
        ('registration', 'Registration Gift'),
        ('purchase', 'Purchase'),
    ], default='registration')

    def activate(self, ip_address):
        """Mark token active, set expiry, whitelist IP in nftables.
        
        Note: Only one token can be active per user at a time.
        If user has an existing active token, it will be expired first.
        """
        # Check for existing active tokens for this user - expire them first
        existing_active = Token.objects.filter(
            user=self.user,
            used=True,
            expired=False,
            expires_at__gt=timezone.now()
        )
        
        for old_token in existing_active:
            old_token.expired = True
            old_token.save()
            # Close associated analytics session if it exists (avoid circular import)
            try:
                from apps.analytics.models import Session
                session = old_token.session
                if session and not session.end_time:
                    session.end_time = timezone.now()
                    session.save()
            except Exception:
                pass
        
        self.used = True
        self.activated_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(hours=settings.TOKEN_DURATION_HOURS)
        self.save()
        # Open firewall for this IP
        seconds = settings.TOKEN_DURATION_HOURS * 3600
        subprocess.run([
            'nft', 'add', 'element', 'ip', 'nat', 'allowed_ips',
            f'{{ {ip_address} timeout {seconds}s }}'
        ], check=False)
        subprocess.run([
            'nft', 'add', 'element', 'ip', 'filter', 'allowed_ips',
            f'{{ {ip_address} timeout {seconds}s }}'
        ], check=False)

    @property
    def is_active(self):
        if not self.used:
            return False
        if self.expired:
            return False
        if not self.expires_at:
            return False
        return timezone.now() < self.expires_at

    def __str__(self):
        return f'Token {str(self.id)[:8]} — {self.user.email}'


class TokenPurchase(models.Model):
    """Records a token purchase transaction."""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def fulfil(self):
        """Create tokens after successful payment confirmation."""
        for _ in range(self.quantity):
            Token.objects.create(user=self.user, source='purchase')
        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        self.save()