from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WebmartUser
from apps.tokens.models import Token


@receiver(post_save, sender=WebmartUser)
def create_initial_tokens(sender, instance, created, **kwargs):
    """Create five tokens for every newly registered user."""
    if created:
        Token.objects.bulk_create([Token(user=instance, source='registration') for _ in range(5)])