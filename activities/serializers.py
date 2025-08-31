
from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Activity
        fields = ['id', 'user', 'activity_type', 'duration', 'distance', 
                 'calories_burned', 'date', 'notes', 'created_at', 'updated_at']

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        return value

    def validate_distance(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Distance cannot be negative.")
        return value

    def validate_calories_burned(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Calories burned must be greater than 0.")
        return value
