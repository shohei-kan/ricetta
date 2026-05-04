from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category, Membership, Shop, Unit
from .seed_data import DEFAULT_UNITS


class ApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = self.create_user("owner@example.com", "password", "山田", "太郎")
        self.other_owner = self.create_user("other@example.com", "password", "佐藤", "花子")
        self.shop = Shop.objects.create(name="〇〇食堂", business_type="カフェ")
        self.other_shop = Shop.objects.create(name="別店舗", business_type="バー")
        self.membership = Membership.objects.create(
            user=self.owner,
            shop=self.shop,
            role=Membership.Role.OWNER,
            display_name="山田 太郎",
        )
        Membership.objects.create(
            user=self.other_owner,
            shop=self.other_shop,
            role=Membership.Role.OWNER,
            display_name="佐藤 花子",
        )

    def create_user(self, email, password, first_name="", last_name=""):
        User = get_user_model()
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return user

    def login_owner(self):
        logged_in = self.client.login(username="owner@example.com", password="password")
        self.assertTrue(logged_in)


class AuthApiTests(ApiTestCase):
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

    def test_logout(self):
        self.login_owner()

        response = self.client.post(reverse("auth_logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "ログアウトしました。")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_me_requires_login(self):
        response = self.client.get(reverse("auth_me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ShopScopeTests(ApiTestCase):
    def test_shop_me_returns_current_users_shop_only(self):
        self.login_owner()

        response = self.client.get(reverse("shop_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.shop.id)
        self.assertNotEqual(response.data["id"], self.other_shop.id)

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


class CategoryApiTests(ApiTestCase):
    def test_category_list_is_scoped_to_current_shop(self):
        self.login_owner()
        Category.objects.create(shop=self.shop, name="仕込み")
        Category.objects.create(shop=self.other_shop, name="別店舗カテゴリ")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data]
        self.assertEqual(names, ["仕込み"])

    def test_category_create_sets_current_shop(self):
        self.login_owner()

        response = self.client.post(
            reverse("category-list"),
            {"name": "ソース", "sort_order": 10, "shop": self.other_shop.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=response.data["id"])
        self.assertEqual(category.shop, self.shop)
        self.assertEqual(category.name, "ソース")


class UnitApiTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        for sort_order, (name, unit_type) in enumerate(DEFAULT_UNITS[:2], start=1):
            Unit.objects.create(
                shop=None,
                name=name,
                unit_type=unit_type,
                is_default=True,
                sort_order=sort_order,
            )

    def test_unit_list_includes_standard_and_current_shop_units(self):
        self.login_owner()
        Unit.objects.create(shop=self.shop, name="皿", unit_type=Unit.UnitType.COUNT, sort_order=10)
        Unit.objects.create(shop=self.other_shop, name="箱", unit_type=Unit.UnitType.COUNT, sort_order=11)

        response = self.client.get(reverse("unit-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data]
        self.assertEqual(names, ["g", "kg", "皿"])

    def test_standard_unit_cannot_be_updated(self):
        self.login_owner()
        standard_unit = Unit.objects.get(name="g")

        response = self.client.patch(
            reverse("unit-detail", args=[standard_unit.id]),
            {"name": "gram"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        standard_unit.refresh_from_db()
        self.assertEqual(standard_unit.name, "g")

    def test_shop_unit_can_be_updated(self):
        self.login_owner()
        shop_unit = Unit.objects.create(shop=self.shop, name="皿", unit_type=Unit.UnitType.COUNT)

        response = self.client.patch(
            reverse("unit-detail", args=[shop_unit.id]),
            {"name": "プレート"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        shop_unit.refresh_from_db()
        self.assertEqual(shop_unit.name, "プレート")
