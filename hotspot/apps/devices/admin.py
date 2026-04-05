from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'user', 'device_type', 'ip_address', 'first_seen', 'last_seen')
    search_fields = ('mac_address', 'user__email', 'device_type')
    list_filter = ('device_type',)