from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.analytics.models import Session


class Command(BaseCommand):
    help = 'Clean up old sessions (e.g., older than 90 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete sessions older than this many days'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff = timezone.now() - timezone.timedelta(days=days)
        old_sessions = Session.objects.filter(start_time__lt=cutoff)
        count = old_sessions.count()
        old_sessions.delete()
        self.stdout.write(f'Deleted {count} sessions older than {days} days.')