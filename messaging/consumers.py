import json
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import ActiveConnection, ChatRoom, ChatUser, Message


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.room_group_name = None
        self.user = None
        self.user_id = None

    async def connect(self):
        try:
            # Get room_id from URL route
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
            self.room_group_name = f"chat_{self.room_id}"

            # Get user info from query parameters
            query_params = (
                dict(self.scope["query_string"].decode().split("&"))
                if self.scope["query_string"]
                else {}
            )
            username = query_params.get("username", "অতিথি")
            color = query_params.get("color", "#007bff")
            session_id = query_params.get("session_id", str(uuid.uuid4()))

            # Create or get user
            self.user = await self.get_or_create_user(username, color, session_id)
            self.user_id = str(self.user.id)

            # Get or create room
            room = await self.get_or_create_room()

            # Check if room is full
            online_count = await self.get_online_users_count()
            if online_count >= room.max_users:
                await self.close(code=4001)
                return

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()

            # Update user status
            await self.update_user_status(True, room)

            # Save connection
            await self.save_connection(room)

            # Send welcome message
            welcome_message = f"{username} চ্যাটরুমে যোগ দিয়েছেন!"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "system_message",
                    "message": welcome_message,
                    "user_id": str(self.user.id),
                    "username": username,
                    "timestamp": timezone.now().isoformat(),
                },
            )

            # Send user list to everyone
            await self.send_user_list()

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if self.room_group_name and self.user:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

            # Update user status
            await self.update_user_status(False, None)

            # Remove connection
            await self.remove_connection()

            # Send leave message
            if close_code != 4001:  # Don't send message if room was full
                leave_message = f"{self.user.username} চ্যাটরুম ছেড়েছেন"
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "system_message",
                        "message": leave_message,
                        "user_id": str(self.user.id),
                        "username": self.user.username,
                        "timestamp": timezone.now().isoformat(),
                    },
                )

                # Update user list
                await self.send_user_list()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "message":
                content = data.get("content", "").strip()
                if content:
                    # Save message
                    message_id = await self.save_message(content)

                    # Broadcast message
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": content,
                            "user_id": self.user_id,
                            "username": self.user.username,
                            "user_color": self.user.color,
                            "message_id": str(message_id),
                            "timestamp": timezone.now().isoformat(),
                        },
                    )

            elif message_type == "typing":
                is_typing = data.get("typing", False)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_indicator",
                        "user_id": self.user_id,
                        "username": self.user.username,
                        "typing": is_typing,
                        "timestamp": timezone.now().isoformat(),
                    },
                )

            elif message_type == "user_update":
                new_username = data.get("username", "").strip()
                new_color = data.get("color", self.user.color)

                if new_username and new_username != self.user.username:
                    old_username = self.user.username
                    await self.update_user_info(new_username, new_color)

                    # Notify everyone about username change
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "system_message",
                            "message": f"{old_username} এখন {new_username} নামে পরিচিত",
                            "user_id": self.user_id,
                            "username": new_username,
                            "timestamp": timezone.now().isoformat(),
                        },
                    )

                    # Update user list
                    await self.send_user_list()

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Receive error: {e}")

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "user_color": event["user_color"],
                    "message_id": event["message_id"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def system_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "system",
                    "message": event["message"],
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def typing_indicator(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "typing": event["typing"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_list_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_list",
                    "users": event["users"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    # Database operations
    @database_sync_to_async
    def get_or_create_user(self, username, color, session_id):
        user, created = ChatUser.objects.get_or_create(
            session_id=session_id,
            defaults={
                "username": username,
                "color": color,
                "is_online": True,
            },
        )
        if not created:
            user.username = username
            user.color = color
            user.is_online = True
            user.save()
        return user

    @database_sync_to_async
    def get_or_create_room(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            # Create a new room if it doesn't exist
            room = ChatRoom.objects.create(
                id=self.room_id, name=f"Room {self.room_id[:8]}", is_public=True
            )
        return room

    @database_sync_to_async
    def get_online_users_count(self):
        return ActiveConnection.objects.filter(room_id=self.room_id).count()

    @database_sync_to_async
    def update_user_status(self, is_online, room):
        self.user.is_online = is_online
        self.user.current_room = room
        self.user.last_seen = timezone.now()
        self.user.save()

    @database_sync_to_async
    def save_connection(self, room):
        ActiveConnection.objects.create(
            user=self.user, channel_name=self.channel_name, room=room
        )

    @database_sync_to_async
    def remove_connection(self):
        ActiveConnection.objects.filter(
            user=self.user, channel_name=self.channel_name
        ).delete()

    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room, user=self.user, content=content, message_type="text"
        )
        return message.id

    @database_sync_to_async
    def update_user_info(self, new_username, new_color):
        self.user.username = new_username
        self.user.color = new_color
        self.user.save()

    @database_sync_to_async
    def get_online_users(self):
        connections = ActiveConnection.objects.filter(
            room_id=self.room_id
        ).select_related("user")
        users = []
        for conn in connections:
            users.append(
                {
                    "id": str(conn.user.id),
                    "username": conn.user.username,
                    "color": conn.user.color,
                    "joined_at": conn.connected_at.isoformat(),
                }
            )
        return users

    async def send_user_list(self):
        users = await self.get_online_users()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_list_update",
                "users": users,
                "timestamp": timezone.now().isoformat(),
            },
        )
