from django.urls import path

from . import views

urlpatterns = [
    path("record/", views.record_interaction, name="record_interaction"),
    path("popular/", views.get_popular_items, name="get_popular_items"),
]
