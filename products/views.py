from rest_framework import generics

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    View to list all products or create a new one.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update or delete a product instance.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
