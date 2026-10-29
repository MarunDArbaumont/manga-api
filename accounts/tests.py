from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient


class LoginThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_login_is_rate_limited(self):
        for _ in range(5):
            response = self.client.post(
                "/api/auth/login/",
                {"username": "missing", "password": "wrong"},
                format="json",
            )
            self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/auth/login/",
            {"username": "missing", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, 429)
