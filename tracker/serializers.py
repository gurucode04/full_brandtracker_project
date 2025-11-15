from rest_framework import serializers
from .models import Mention, Alert

class MentionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ', read_only=True)
    fetched_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ', read_only=True)
    
    class Meta:
        model = Mention
        fields = '__all__'
        read_only_fields = ('fetched_at',)

class AlertSerializer(serializers.ModelSerializer):
    mention = MentionSerializer(read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ('created_at',)
