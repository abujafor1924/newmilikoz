from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product
from .serializers import ProductSerializer


class ProductAPITests(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name="Product 1", price="10.00")
        self.product2 = Product.objects.create(name="Product 2", price="20.00")
        self.valid_payload = {"name": "New Product", "price": "30.00"}
        self.invalid_payload = {"name": "", "price": "40.00"}

    def test_get_all_products(self):
        url = reverse("product-list-create")
        response = self.client.get(url)
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_valid_product(self):
        url = reverse("product-list-create")
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_create_invalid_product(self):
        url = reverse("product-list-create")
        response = self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_valid_single_product(self):
        url = reverse("product-detail", kwargs={"pk": self.product1.pk})
        response = self.client.get(url)
        product = Product.objects.get(pk=self.product1.pk)
        serializer = ProductSerializer(product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_single_product(self):
        url = reverse("product-detail", kwargs={"pk": 30})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_update_product(self):
        url = reverse("product-detail", kwargs={"pk": self.product1.pk})
        response = self.client.put(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, self.valid_payload["name"])

    def test_invalid_update_product(self):
        url = reverse("product-detail", kwargs={"pk": self.product1.pk})
        response = self.client.put(url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_product(self):
        url = reverse("product-detail", kwargs={"pk": self.product1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)
