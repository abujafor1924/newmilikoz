# products/services.py
from .models import Product
from .serializers import ProductSerializer


class ProductService:
    """
    This service class encapsulates the business logic for creating and updating products.
    By having a dedicated service, we follow the Single Responsibility Principle.
    The view doesn't need to know how a product is created, only that it can be.
    This also follows the Dependency Inversion Principle, as the view will depend on this
    service (an abstraction) rather than the low-level model details.
    """

    def create_product(self, data: dict) -> Product:
        """
        Creates a new product.
        The data is a dictionary of validated data from a serializer.
        """
        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        # In a real-world application, you might have more logic here,
        # like sending a notification, updating other models, etc.
        return product

    def update_product(self, product: Product, data: dict) -> Product:
        """
        Updates an existing product.
        """
        serializer = ProductSerializer(instance=product, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_product = serializer.save()
        return updated_product
