THROTTLE_CONFIG = {
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.analytics.throttles.BurstThrottle",
        "apps.analytics.throttles.SustainedThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "burst": "30/second",
        "sustained": "1000/hour",
        "finance": "100/minute",
        "ai": "20/minute",
        "anonymous": "10/minute",
    },
}
