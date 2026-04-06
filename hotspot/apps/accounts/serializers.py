from rest_framework import serializers
from .models import WebmartUser, phone_regex


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=13, required=False, validators=[phone_regex])
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = WebmartUser
        fields = ['username', 'email', 'password', 'phone']

    def create(self, validated_data):
        # Auto-generate username from email if not provided
        username = validated_data.get('username') or validated_data.get('email', '')
        if '@' in username:
            username = username.split('@')[0]
        validated_data['username'] = username
        return WebmartUser.objects.create_user(**validated_data)


class WebmartUserSerializer(serializers.ModelSerializer):
    available_tokens = serializers.IntegerField(read_only=True)

    class Meta:
        model = WebmartUser
        fields = ['id', 'username', 'email', 'phone', 'available_tokens']