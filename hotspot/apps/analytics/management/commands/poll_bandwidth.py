from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.analytics.models import Session
import subprocess


class Command(BaseCommand):
    help = 'Poll nftables counters and update session bandwidth'

    def handle(self, *args, **kwargs):
        active = Session.objects.filter(end_time__isnull=True)
        for session in active:
            ip = session.ip_address
            rx = self._get_bytes('input', ip)
            tx = self._get_bytes('output', ip)
            session.bytes_rx = rx
            session.bytes_tx = tx
            # Close expired sessions
            if session.token and not session.token.is_active:
                session.end_time = timezone.now()
            session.save()

    def _get_bytes(self, direction, ip):
        try:
            result = subprocess.run(
                ['nft', '-j', 'list', 'ruleset'],
                capture_output=True, text=True
            )
            # Parse JSON output for counter matching IP
            # This is a simplified placeholder - production should parse properly
            return 0
        except Exception:
            return 0