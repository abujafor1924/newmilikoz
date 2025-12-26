from rest_framework import serializers

from .models import ActiveConnection, ChatRoom, ChatUser, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    online_users_count = serializers.IntegerField(read_only=True)
    total_messages_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "max_users",
            "online_users_count",
            "total_messages_count",
            "created_at",
        ]


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ["id", "username", "color", "is_online", "last_seen", "created_at"]
        read_only_fields = ["id", "is_online", "last_seen", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    user = ChatUserSerializer(read_only=True)
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())

    class Meta:
        model = Message
        fields = [
            "id",
            "room",
            "user",
            "content",
            "message_type",
            "file_url",
            "timestamp",
        ]
        read_only_fields = ["user", "timestamp"]


class ActiveConnectionSerializer(serializers.ModelSerializer):
    user = ChatUserSerializer(read_only=True)

    class Meta:
        model = ActiveConnection
        fields = ["id", "user", "channel_name", "room", "connected_at"]


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    color = serializers.CharField(max_length=7, required=False, default="#007bff")

    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("ইউজারনেম ফাঁকা হতে পারবে না")
        return value.strip()


class JoinRoomSerializer(serializers.Serializer):
    room_id = serializers.UUIDField()
    username = serializers.CharField(max_length=100)
    color = serializers.CharField(max_length=7, required=False, default="#007bff")
