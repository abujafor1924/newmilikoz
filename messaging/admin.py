from django.contrib import admin

from .models import ActiveConnection, ChatRoom, ChatUser, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_public",
        "max_users",
        "created_at",
        "online_users_count",
    ]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "description"]

    def online_users_count(self, obj):
        return obj.online_users_count

    online_users_count.short_description = "অনলাইন ব্যবহারকারী"


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "session_id_short",
        "is_online",
        "current_room",
        "last_seen",
    ]
    list_filter = ["is_online", "created_at"]
    search_fields = ["username", "session_id"]

    def session_id_short(self, obj):
        return (
            obj.session_id[:20] + "..." if len(obj.session_id) > 20 else obj.session_id
        )

    session_id_short.short_description = "সেশন আইডি"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["user", "room", "content_short", "message_type", "timestamp"]
    list_filter = ["message_type", "timestamp", "room"]
    search_fields = ["content", "user__username"]

    def content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_short.short_description = "বার্তা"


@admin.register(ActiveConnection)
class ActiveConnectionAdmin(admin.ModelAdmin):
    list_display = ["user", "room", "channel_name_short", "connected_at"]
    list_filter = ["connected_at", "room"]
    search_fields = ["user__username", "channel_name"]

    def channel_name_short(self, obj):
        return (
            obj.channel_name[:30] + "..."
            if len(obj.channel_name) > 30
            else obj.channel_name
        )

    channel_name_short.short_description = "চ্যানেল"
