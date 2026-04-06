from rest_framework import serializers
from .models import WebmartUser, phone_regex


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=13, required=False, validators=[phone_regex])

    class Meta:
        model = WebmartUser
        fields = ['username', 'email', 'password', 'phone']

    def create(self, validated_data):
        # Auto-generate username from email if not provided
        if not validated_data.get('username'):
            email = validated_data.get('email', '')
            validated_data['username'] = email.split('@')[0] if '@' in email else email
        return WebmartUser.objects.create_user(**validated_data)


class WebmartUserSerializer(serializers.ModelSerializer):
    available_tokens = serializers.IntegerField(read_only=True)

    class Meta:
        model = WebmartUser
        fields = ['id', 'username', 'email', 'phone', 'available_tokens']