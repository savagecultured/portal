from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import WebmartUser
from apps.devices.models import Device
from apps.tokens.models import Token
from apps.analytics.models import Session


class DeviceInline(admin.TabularInline):
    model = Device
    fk_name = 'user'
    extra = 0
    readonly_fields = ('mac_address', 'ip_address', 'device_type', 'os_hint', 'first_seen', 'last_seen')


class TokenInline(admin.TabularInline):
    model = Token
    extra = 0
    readonly_fields = ('id', 'source', 'used', 'expired', 'activated_at', 'expires_at', 'created_at')


class SessionInline(admin.TabularInline):
    model = Session
    extra = 0
    readonly_fields = ('start_time', 'end_time', 'ip_address', 'bytes_rx', 'bytes_tx')


@admin.register(WebmartUser)
class WebmartUserAdmin(UserAdmin):
    inlines = [DeviceInline, TokenInline, SessionInline]
    list_display = ('email', 'username', 'phone', 'available_tokens', 'total_sessions', 'date_joined')
    search_fields = ('email', 'username', 'phone')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def available_tokens(self, obj):
        return obj.available_tokens
    available_tokens.short_description = 'Tokens Left'

    def total_sessions(self, obj):
        return Session.objects.filter(user=obj).count()
    total_sessions.short_description = 'Sessions'
