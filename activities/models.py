
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('Running', 'Running'),
        ('Cycling', 'Cycling'),
        ('Swimming', 'Swimming'),
        ('Weightlifting', 'Weightlifting'),
        ('Yoga', 'Yoga'),
        ('Walking', 'Walking'),
        ('Hiking', 'Hiking'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    distance = models.FloatField(blank=True, null=True, help_text="Distance in kilometers")
    calories_burned = models.PositiveIntegerField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.date.strftime('%Y-%m-%d')}"

    def clean(self):
        if self.duration <= 0:
            raise ValidationError({'duration': 'Duration must be greater than 0.'})

        if self.distance is not None and self.distance < 0:
            raise ValidationError({'distance': 'Distance cannot be negative.'})

        if self.calories_burned is not None and self.calories_burned <= 0:
            raise ValidationError({'calories_burned': 'Calories burned must be greater than 0.'})
