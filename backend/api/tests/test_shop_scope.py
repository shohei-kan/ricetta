# pyright: reportAttributeAccessIssue=false

from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from api.models import Category, Membership, Unit

from .base import ApiTestCase


class ShopScopeTests(ApiTestCase):
    def test_shop_me_returns_current_users_shop_only(self):
        self.login_owner()

        response = self.client.get(reverse("shop_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.shop.id)
        self.assertNotEqual(response.data["id"], self.other_shop.id)

    def test_owner_can_update_current_shop(self):
        self.login_owner()

        response = self.client.patch(
            reverse("shop_me"),
            {
                "name": "新しい食堂名",
                "business_type": "定食屋",
                "memo": "駅前店舗",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.name, "新しい食堂名")
        self.assertEqual(self.shop.business_type, "定食屋")
        self.assertEqual(self.shop.memo, "駅前店舗")

    @override_settings(DEMO_MODE=True)
    def test_demo_mode_keeps_owner_shop_update_allowed(self):
        self.login_owner()

        response = self.client.patch(
            reverse("shop_me"),
            {"memo": "公開デモでも店舗メモ編集はownerに許可"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.memo, "公開デモでも店舗メモ編集はownerに許可")

    def test_staff_cannot_update_current_shop(self):
        staff = self.create_user("staff@example.com", "password")
        Membership.objects.create(
            user=staff,
            shop=self.shop,
            role=Membership.Role.STAFF,
            display_name="スタッフ",
        )
        self.client.login(username="staff@example.com", password="password")

        response = self.client.patch(
            reverse("shop_me"),
            {"name": "変更できない店舗名"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.name, "〇〇食堂")

    def test_cannot_access_other_shop_category(self):
        self.login_owner()
        other_category = Category.objects.create(shop=self.other_shop, name="秘密カテゴリ")

        response = self.client.patch(
            reverse("category-detail", args=[other_category.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_category.refresh_from_db()
        self.assertEqual(other_category.name, "秘密カテゴリ")

    def test_cannot_access_other_shop_unit(self):
        self.login_owner()
        other_unit = Unit.objects.create(shop=self.other_shop, name="箱", unit_type=Unit.UnitType.COUNT)

        response = self.client.patch(
            reverse("unit-detail", args=[other_unit.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_unit.refresh_from_db()
        self.assertEqual(other_unit.name, "箱")
