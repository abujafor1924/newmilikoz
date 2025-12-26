from django.urls import include, path

from book import views as book_view
from crudoparetions import views as oparetions
from messaging import views as messaging_view
from userauth import views as userauth_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'rooms',messaging_view.ChatRoomViewSet, basename='rooms')
router.register(r'messages',messaging_view.MessageViewSet, basename='messages')

urlpatterns = [
    # Example endpoints
    path(
        "register/",
        userauth_views.ReagistrationUserAPIView.as_view(),
        name="user-register",
    ),
    path("login/", userauth_views.LoginUserAPIView.as_view(), name="user-login"),
    path(
        "reset-password/",
        userauth_views.RequistPasswordResetAPIView.as_view(),
        name="reset-password",
    ),
    path(
        "verify-otp/", userauth_views.ResetOtpVerifyAPIView.as_view(), name="verify-otp"
    ),
    path(
        "confirm-reset-password/",
        userauth_views.PasswordResetConfirmAPIView.as_view(),
        name="confirm-reset-password",
    ),
    path("profile/", userauth_views.UserProfileAPIView.as_view(), name="user-profile"),
    # intarections APPS
    path("interactions", include("interactions.urls")),
    # Books View Api Collections
    path("bookview/", book_view.BookListAPIView.as_view(), name="book-list-api-view"),
    path(
        "books/<int:id>/",
        book_view.BookRetrieveUpdateDestroyAPIView.as_view(),
        name="book-detail",
    ),
    # Oparetions testing
    path("oparetions/", oparetions.BookListAPIView.as_view(), name="crud oparetions"),
    path(
        "oparetions/<int:pk>/",
        oparetions.BookDetailAPIView.as_view(),
        name="book-detail-update-delete",
    ),
    # Custom operations
    path(
        "oparetions-list/operations/",
        oparetions.BookOperationsView.as_view(),
        name="book-operations",
    ),
    path(
        "oparetions-list/operations/<int:pk>/",
        oparetions.BookOperationsView.as_view(),
        name="book-specific-operations",
    ),
    # Search
    path(
        "oparetions-list/search/",
        oparetions.BookSearchView.as_view(),
        name="book-search",
    ),
    # Chat App
     # Router URLs
    path('', include(router.urls)),
    
    # User management
    path('create-user/', messaging_view.CreateUserView.as_view(), name='create_user'),
    path('join-room/', messaging_view.JoinRoomView.as_view(), name='join_room'),
    
    # Public rooms
    path('public-rooms/', messaging_view.PublicRoomsView.as_view(), name='public_rooms'),
    path('rooms/<uuid:room_id>/stats/', messaging_view.RoomStatsView.as_view(), name='room_stats'),
    
    # System status
    path('status/', messaging_view.system_status, name='system_status'),
    
]
