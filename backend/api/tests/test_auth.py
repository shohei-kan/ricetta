# pyright: reportAttributeAccessIssue=false

import base64

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Membership

from .base import ApiTestCase


class AuthApiTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_health_check_allows_anonymous_access(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    def test_health_check_allows_authenticated_access(self):
        self.login_owner()

        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    def test_csrf_sets_cookie(self):
        response = self.client.get(reverse("auth_csrf"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "CSRF cookie set.")
        self.assertIn("csrftoken", self.client.cookies)

    def test_login_with_development_owner_shape(self):
        response = self.client.post(
            reverse("auth_login"),
            {"email": "owner@example.com", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "owner@example.com")
        self.assertEqual(response.data["user"]["name"], "山田 太郎")
        self.assertEqual(response.data["shop"]["id"], self.shop.id)
        self.assertEqual(response.data["membership"]["role"], "owner")

    def test_staff_login_succeeds(self):
        self.create_staff_membership()

        response = self.client.post(
            reverse("auth_login"),
            {"email": "staff@example.com", "password": "password"},
            format="json",
            REMOTE_ADDR="192.0.2.10",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["membership"]["role"], "staff")

    def test_login_failures_return_the_same_generic_response(self):
        inactive = self.create_user("inactive@example.com", "password")
        inactive.is_active = False
        inactive.save(update_fields=["is_active"])
        attempts = [
            {"email": "missing@example.com", "password": "password"},
            {"email": "owner@example.com", "password": "wrong-password"},
            {"email": "inactive@example.com", "password": "password"},
        ]

        responses = [
            self.client.post(
                reverse("auth_login"),
                payload,
                format="json",
                REMOTE_ADDR="192.0.2.11",
            )
            for payload in attempts
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(responses[0].data, responses[1].data)
        self.assertEqual(responses[1].data, responses[2].data)

    def test_login_is_throttled_after_five_attempts_per_ip(self):
        for _attempt in range(5):
            response = self.client.post(
                reverse("auth_login"),
                {"email": "missing@example.com", "password": "wrong-password"},
                format="json",
                REMOTE_ADDR="192.0.2.12",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        throttled = self.client.post(
            reverse("auth_login"),
            {"email": "missing@example.com", "password": "wrong-password"},
            format="json",
            REMOTE_ADDR="192.0.2.12",
        )

        self.assertEqual(throttled.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_basic_authentication_is_not_accepted(self):
        credentials = base64.b64encode(b"owner@example.com:password").decode("ascii")

        response = self.client.get(
            reverse("auth_me"),
            HTTP_AUTHORIZATION=f"Basic {credentials}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_after_login(self):
        self.login_owner()

        response = self.client.get(reverse("auth_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["shop"]["name"], "〇〇食堂")
        self.assertEqual(response.data["membership"]["role"], "owner")
        self.assertEqual(response.data["membership"]["display_name"], "山田 太郎")

    def test_owner_can_update_own_display_name(self):
        self.login_owner()

        response = self.client.patch(
            reverse("auth_me"),
            {"display_name": "山田 店長"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.display_name, "山田 店長")
        self.assertEqual(response.data["membership"]["display_name"], "山田 店長")

    def test_staff_can_update_own_display_name(self):
        staff = self.create_user("staff@example.com", "password")
        membership = Membership.objects.create(
            user=staff,
            shop=self.shop,
            role=Membership.Role.STAFF,
            display_name="スタッフ",
        )
        self.client.login(username="staff@example.com", password="password")

        response = self.client.patch(
            reverse("auth_me"),
            {"display_name": "佐藤 スタッフ"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        membership.refresh_from_db()
        self.assertEqual(membership.display_name, "佐藤 スタッフ")
        self.assertEqual(response.data["membership"]["role"], "staff")

    @override_settings(DEMO_MODE=True)
    def test_demo_mode_allows_own_display_name_update(self):
        self.login_owner()

        response = self.client.patch(
            reverse("auth_me"),
            {"display_name": "デモ店長"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.display_name, "デモ店長")

    def test_logout(self):
        self.login_owner()

        response = self.client.post(reverse("auth_logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "ログアウトしました。")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_me_requires_login(self):
        response = self.client.get(reverse("auth_me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_still_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_authenticated_unsafe_request_still_requires_csrf(self):
        csrf_client = APIClient(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)

        without_token = csrf_client.patch(
            reverse("auth_me"),
            {"display_name": "CSRFなし"},
            format="json",
        )
        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)

        csrf_client.get(reverse("auth_csrf"))
        csrf_token = csrf_client.cookies["csrftoken"].value
        with_token = csrf_client.patch(
            reverse("auth_me"),
            {"display_name": "CSRFあり"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    )
    def test_health_check_accepts_internal_http_with_forwarded_https_header(self):
        response = self.client.get(
            reverse("health_check"),
            HTTP_X_FORWARDED_PROTO="https",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
