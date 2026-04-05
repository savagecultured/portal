from django.contrib import admin
from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'ip_address', 'start_time', 'end_time', 'duration', 'bandwidth')
    readonly_fields = ('bytes_rx', 'bytes_tx')

    def duration(self, obj):
        d = obj.duration_seconds
        return f'{d//3600}h {(d%3600)//60}m'
    duration.short_description = 'Time Spent'

    def bandwidth(self, obj):
        mb = obj.total_bytes / (1024*1024)
        return f'{mb:.2f} MB'
    bandwidth.short_description = 'Bandwidth'