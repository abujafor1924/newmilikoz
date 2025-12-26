import json
import logging

logger = logging.getLogger("django")


class APILogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Request details
        try:
            body = json.loads(request.body)
        except:
            body = request.body.decode("utf-8") if request.body else {}

        logger.info(f"API Request: {request.method} {request.path} | Body: {body}")

        # Response
        response = self.get_response(request)

        try:
            content = response.content.decode("utf-8")
            if len(content) > 500:  # Limit response length
                content = content[:500] + "..."
        except:
            content = str(response)

        logger.info(
            f"API Response: {request.method} {request.path} | Status: {response.status_code} | Response: {content}"
        )

        return response
