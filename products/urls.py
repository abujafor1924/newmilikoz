from django.urls import path

from .views import ProductDetailAPIView, ProductListCreateAPIView

urlpatterns = [
    path("", ProductListCreateAPIView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
]
