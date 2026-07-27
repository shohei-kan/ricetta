# pyright: reportAttributeAccessIssue=false

from django.urls import reverse
from rest_framework import status

from api.models import Category

from .base import ApiTestCase


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

    def test_owner_can_update_category(self):
        self.login_owner()
        category = Category.objects.create(shop=self.shop, name="仕込み")

        response = self.client.patch(
            reverse("category-detail", args=[category.id]),
            {"name": "ソース"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "ソース")

    def test_owner_can_delete_category(self):
        self.login_owner()
        category = Category.objects.create(shop=self.shop, name="仕込み")

        response = self.client.delete(reverse("category-detail", args=[category.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        category.refresh_from_db()
        self.assertFalse(category.is_active)

    def test_staff_can_view_categories(self):
        self.login_staff()
        Category.objects.create(shop=self.shop, name="仕込み")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data], ["仕込み"])

    def test_staff_cannot_create_category(self):
        self.login_staff()

        response = self.client.post(
            reverse("category-list"),
            {"name": "ソース"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Category.objects.filter(shop=self.shop, name="ソース").exists())

    def test_staff_cannot_update_category(self):
        self.login_staff()
        category = Category.objects.create(shop=self.shop, name="仕込み")

        response = self.client.patch(
            reverse("category-detail", args=[category.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        category.refresh_from_db()
        self.assertEqual(category.name, "仕込み")

    def test_staff_cannot_delete_category(self):
        self.login_staff()
        category = Category.objects.create(shop=self.shop, name="仕込み")

        response = self.client.delete(reverse("category-detail", args=[category.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        category.refresh_from_db()
        self.assertTrue(category.is_active)
