from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    """Limit login attempts by client IP, whether authenticated or not."""

    scope = "login"
    rate = "5/min"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
