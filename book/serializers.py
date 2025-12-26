from django.utils import timezone
from rest_framework import serializers

from .models import Book


class BookSerializers(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

    def validate_publish(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "The publishing date cannot be in the future."
            )
        return value
