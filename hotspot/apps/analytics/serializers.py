from rest_framework import serializers
from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Session
        fields = ['id', 'user', 'device', 'token', 'start_time', 'end_time', 'bytes_rx', 'bytes_tx', 'ip_address', 'duration_seconds', 'total_bytes']
        read_only_fields = fields