import time

from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Imagine you have a Celery task defined somewhere for asynchronous processing
# from .tasks import process_interaction_task


@api_view(["POST"])
def record_interaction(request):
    """
    Records a user interaction, like a "like", "view", or "click".

    SCALABILITY STRATEGY:
    For high-traffic sites, writing to the database on every request can become a
    bottleneck. A common pattern is to offload this work to a background task.

    1. Asynchronous Task Queue (e.g., Celery with Redis/RabbitMQ):
       Instead of writing directly to the database here, we would queue a task.
       This view would return an immediate "202 Accepted" response, making the
       user experience fast. The background worker then processes the task,
       updating the database.

       Example:
       user_id = request.user.id
       item_id = request.data.get('item_id') # Use request.data with DRF
       # process_interaction_task.delay(user_id, item_id) # This is a non-blocking call

    2. Database Optimization:
       The database table for interactions should be designed for fast writes.
       - Use a simple structure.
       - Avoid complex constraints or triggers if possible during the write.
       - If using a relational database, ensure indexes are in place on foreign keys
         (e.g., user_id, item_id).
    """
    # For demonstration, we'll just simulate a quick response.
    # In a real high-concurrency scenario, the following line would be a
    # call to a Celery task.
    # process_interaction_task.delay(user_id, item_id)
    return Response({"status": "accepted"}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def get_popular_items(request):
    """
    Retrieves a list of popular items. This could be based on likes, views, etc.

    SCALABILITY STRATEGY:
    Calculating popularity scores and aggregating data is often a slow process.
    Doing this on every request is not feasible for a high-traffic endpoint.

    1. Caching (e.g., Redis, Memcached):
       The results of this query should be cached. The first time the view is
       hit, it computes the data, stores it in the cache with a timeout (e.g., 5 minutes),
       and then serves it. Subsequent requests will get the data directly from
       the cache, which is extremely fast.

    2. Pre-computation / Materialized Views:
       A background job (e.g., a cron job or a periodic Celery task) can
       pre-calculate the list of popular items and store it in a simple,
       denormalized table or in the cache. This view would then just be a
       simple, fast read from that pre-computed store.
    """
    cache_key = "popular_items_list"
    popular_items = cache.get(cache_key)

    if popular_items is None:
        # Simulate a slow database query/calculation
        time.sleep(1)  # Simulating a 1-second database query
        popular_items = [
            {"id": 1, "name": "Popular Item 1", "score": 1024},
            {"id": 2, "name": "Popular Item 2", "score": 987},
            {"id": 3, "name": "Popular Item 3", "score": 850},
        ]
        # Cache the result for 5 minutes (300 seconds)
        cache.set(cache_key, popular_items, 300)

    return Response(popular_items)
