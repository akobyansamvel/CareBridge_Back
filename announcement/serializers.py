from rest_framework import serializers
from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.email')

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'geolocation', 'task_type', 'preferred_gender', 'urgency', 'creator', 'created_at', 'updated_at']
        read_only_fields = ['creator', 'created_at', 'updated_at']