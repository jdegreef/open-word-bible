"""Rate limits for the API's open reads, counted by the address Render saw
(accounts.views.client_ip), not by the X-Forwarded-For a client can write
itself, which is what DRF counts by default (NUM_PROXIES unset)."""
from rest_framework.throttling import UserRateThrottle

from accounts.views import client_ip


class ApiThrottle(UserRateThrottle):
    """Per account when signed in, else per address: settings
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"][scope]."""

    def get_ident(self, request):
        return client_ip(request) or super().get_ident(request)


class ReadThrottle(ApiThrottle):
    """The Bible text, sentence records, editions and like counts."""
    scope = "read"
