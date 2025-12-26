import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_example_view_get(client):
    url = reverse(
        "api:example-list"
    )  # Assuming you have a URL named 'example-list' in your api app
    response = client.get(url)
    assert response.status_code == 200
    assert "Welcome to the API!" in response.content.decode()


@pytest.mark.django_db
def test_another_example():
    assert 1 + 1 == 2
