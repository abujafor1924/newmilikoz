import uuid

from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    max_users = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def online_users_count(self):
        return ChatUser.objects.filter(current_room=self, is_online=True).count()

    @property
    def total_messages_count(self):
        return Message.objects.filter(room=self).count()


class ChatUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#007bff")  # Hex color
    is_online = models.BooleanField(default=False)
    current_room = models.ForeignKey(
        ChatRoom, on_delete=models.SET_NULL, null=True, blank=True
    )
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.session_id[:8]})"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user = models.ForeignKey(
        ChatUser, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    message_type = models.CharField(
        max_length=20,
        default="text",
        choices=[
            ("text", "Text"),
            ("image", "Image"),
            ("file", "File"),
            ("system", "System"),
        ],
    )
    file_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class ActiveConnection(models.Model):
    user = models.ForeignKey(
        ChatUser, on_delete=models.CASCADE, related_name="connections"
    )
    channel_name = models.CharField(max_length=255)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    connected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.channel_name}"
