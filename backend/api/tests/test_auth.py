# pyright: reportAttributeAccessIssue=false

from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from api.models import Membership

from .base import ApiTestCase


class AuthApiTests(ApiTestCase):
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
