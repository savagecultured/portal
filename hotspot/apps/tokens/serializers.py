from rest_framework import serializers
from .models import Token, TokenPurchase


class TokenSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Token
        fields = ['id', 'user', 'source', 'used', 'expired', 'activated_at', 'expires_at', 'created_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'activated_at', 'expires_at', 'used', 'expired']


class TokenPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPurchase
        fields = ['id', 'user', 'quantity', 'amount', 'currency', 'status', 'reference', 'created_at', 'completed_at']
        read_only_fields = ['id', 'user', 'status', 'created_at', 'completed_at']