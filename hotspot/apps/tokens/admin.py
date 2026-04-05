from django.contrib import admin
from .models import Token, TokenPurchase


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'source', 'used', 'expired', 'activated_at', 'expires_at', 'created_at')
    list_filter = ('source', 'used', 'expired')
    search_fields = ('user__email', 'id')
    readonly_fields = ('id', 'created_at')


@admin.register(TokenPurchase)
class TokenPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'amount', 'currency', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'currency')
    search_fields = ('user__email', 'reference')
    readonly_fields = ('created_at', 'completed_at')