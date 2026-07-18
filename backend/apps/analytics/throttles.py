from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, SimpleRateThrottle


class FinanceActionThrottle(UserRateThrottle):
    scope = "finance"
    rate = "100/minute"

    FINANCIAL_ENDPOINTS = (
        "/api/v1/contracts/",
        "/api/v1/invoices/",
        "/api/v1/billing/",
        "/api/v1/recognition/",
        "/api/v1/collections/",
        "/api/v1/profitability/",
    )

    def allow_request(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if not any(request.path.startswith(ep) for ep in self.FINANCIAL_ENDPOINTS):
            return True
        return super().allow_request(request, view)


class AIServiceThrottle(UserRateThrottle):
    scope = "ai"
    rate = "20/minute"

    def allow_request(self, request, view):
        if not request.path.startswith("/api/v1/ai/"):
            return True
        return super().allow_request(request, view)


class BurstThrottle(UserRateThrottle):
    scope = "burst"
    rate = "30/second"


class SustainedThrottle(UserRateThrottle):
    scope = "sustained"
    rate = "1000/hour"


class AnonymousThrottle(AnonRateThrottle):
    scope = "anonymous"
    rate = "10/minute"
