from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tokens.models import Token
import subprocess


class Command(BaseCommand):
    help = 'Mark expired tokens and remove IPs from nftables'

    def handle(self, *args, **kwargs):
        expired = Token.objects.filter(
            used=True,
            expired=False,
            expires_at__lt=timezone.now()
        )
        count = 0
        for token in expired:
            token.expired = True
            token.save()
            # Close associated analytics session
            try:
                session = token.session
                if session and not session.end_time:
                    session.end_time = timezone.now()
                    session.save()
                    ip = session.ip_address
                    # Remove from nftables
                    subprocess.run(['nft', 'delete', 'element', 'ip', 'nat', 'allowed_ips',
                                    f'{{ {ip} }}'], check=False)
                    subprocess.run(['nft', 'delete', 'element', 'ip', 'filter', 'allowed_ips',
                                    f'{{ {ip} }}'], check=False)
            except Exception:
                pass
            count += 1
        self.stdout.write(f'Expired {count} tokens.')