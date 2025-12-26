# products/selectors.py
from .models import Product


def get_all_products():
    """
    Returns a queryset of all products.
    This is a simple selector, but in a real-world scenario,
    it could contain more complex filtering or ordering logic.
    """
    return Product.objects.all()


def get_product_by_id(product_id: int):
    """
    Returns a single product by its ID.
    """
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None
