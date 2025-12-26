# Create user with session
import uuid

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ActiveConnection, ChatRoom, ChatUser, Message
from .serializers import (ChatRoomSerializer, ChatUserSerializer,
                          CreateUserSerializer, JoinRoomSerializer,
                          MessageSerializer)


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.filter(is_public=True)
    serializer_class = ChatRoomSerializer

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        room = self.get_object()
        messages = Message.objects.filter(room=room).order_by("timestamp")[:100]
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        room = self.get_object()
        # Get active users in this room

        connections = ActiveConnection.objects.filter(room=room).select_related("user")
        users = [conn.user for conn in connections]
        serializer = ChatUserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def popular(self, request):
        rooms = (
            ChatRoom.objects.annotate(user_count=Count("activeconnection"))
            .filter(is_public=True)
            .order_by("-user_count")[:10]
        )
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        room_id = self.request.query_params.get("room_id")
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        return queryset.order_by("-timestamp")[:100]


class CreateUserView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            import uuid

            from django.utils import timezone

            # Create user
            session_id = str(uuid.uuid4())
            user = ChatUser.objects.create(
                session_id=session_id,
                username=serializer.validated_data["username"],
                color=serializer.validated_data.get("color", "#007bff"),
                is_online=True,
                last_seen=timezone.now(),
            )

            return Response(
                {
                    "user_id": str(user.id),
                    "session_id": session_id,
                    "username": user.username,
                    "color": user.color,
                    "message": "ব্যবহারকারী তৈরি করা হয়েছে",
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinRoomView(APIView):
    def post(self, request):
        serializer = JoinRoomSerializer(data=request.data)
        if serializer.is_valid():
            room_id = serializer.validated_data["room_id"]
            username = serializer.validated_data["username"]
            color = serializer.validated_data.get("color", "#007bff")

            # Get or create room
            room, created = ChatRoom.objects.get_or_create(
                id=room_id,
                defaults={"name": f"রুম {str(room_id)[:8]}", "is_public": True},
            )

            session_id = str(uuid.uuid4())
            user = ChatUser.objects.create(
                session_id=session_id,
                username=username,
                color=color,
                is_online=True,
                current_room=room,
                last_seen=timezone.now(),
            )

            return Response(
                {
                    "room_id": str(room.id),
                    "room_name": room.name,
                    "user_id": str(user.id),
                    "session_id": session_id,
                    "username": user.username,
                    "color": user.color,
                    "websocket_url": f"ws://{request.get_host()}/ws/chat/{room.id}/?username={username}&color={color}&session_id={session_id}",
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicRoomsView(APIView):
    def get(self, request):
        rooms = (
            ChatRoom.objects.filter(is_public=True)
            .annotate(
                online_count=Count("activeconnection"), message_count=Count("messages")
            )
            .order_by("-online_count")
        )

        data = []
        for room in rooms:
            data.append(
                {
                    "id": str(room.id),
                    "name": room.name,
                    "description": room.description,
                    "online_users": room.online_count,
                    "total_messages": room.message_count,
                    "max_users": room.max_users,
                    "created_at": room.created_at,
                }
            )

        return Response(data)


class RoomStatsView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        from .models import ActiveConnection

        online_users = ActiveConnection.objects.filter(room=room).count()
        total_messages = Message.objects.filter(room=room).count()

        return Response(
            {
                "room_id": str(room.id),
                "room_name": room.name,
                "online_users": online_users,
                "total_messages": total_messages,
                "max_users": room.max_users,
                "is_public": room.is_public,
                "created_at": room.created_at,
            }
        )


@api_view(["GET"])
def system_status(request):
    from .models import ActiveConnection

    total_rooms = ChatRoom.objects.count()
    total_users = ChatUser.objects.count()
    total_messages = Message.objects.count()
    online_users = ActiveConnection.objects.values("user").distinct().count()
    active_rooms = ActiveConnection.objects.values("room").distinct().count()

    return Response(
        {
            "total_rooms": total_rooms,
            "total_users": total_users,
            "total_messages": total_messages,
            "online_users": online_users,
            "active_rooms": active_rooms,
            "status": "সক্রিয়",
        }
    )
