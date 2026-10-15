import time
from django.contrib.auth import logout

MAX_SESSION_AGE = 60 * 60 * 24 * 30


class AbsoluteSessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            started = request.session.setdefault("login_at", int(time.time()))
            if time.time() - started > MAX_SESSION_AGE:
                logout(request)
        return self.get_response(request)