# pyright: reportAttributeAccessIssue=false

from django.urls import reverse
from rest_framework import status

from api.models import Unit
from api.seed_data import DEFAULT_UNITS

from .base import ApiTestCase


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

    def test_staff_can_view_units(self):
        self.login_staff()
        Unit.objects.create(shop=self.shop, name="皿", unit_type=Unit.UnitType.COUNT, sort_order=10)

        response = self.client.get(reverse("unit-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data]
        self.assertEqual(names, ["g", "kg", "皿"])

    def test_owner_can_create_shop_unit(self):
        self.login_owner()

        response = self.client.post(
            reverse("unit-list"),
            {"name": "ポーション", "unit_type": "custom", "sort_order": 10},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        unit = Unit.objects.get(id=response.data["id"])
        self.assertEqual(unit.shop, self.shop)
        self.assertFalse(unit.is_default)

    def test_staff_cannot_create_unit(self):
        self.login_staff()

        response = self.client.post(
            reverse("unit-list"),
            {"name": "ポーション", "unit_type": "custom"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Unit.objects.filter(shop=self.shop, name="ポーション").exists())

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

    def test_staff_cannot_update_unit(self):
        self.login_staff()
        shop_unit = Unit.objects.create(shop=self.shop, name="皿", unit_type=Unit.UnitType.COUNT)

        response = self.client.patch(
            reverse("unit-detail", args=[shop_unit.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        shop_unit.refresh_from_db()
        self.assertEqual(shop_unit.name, "皿")

    def test_owner_can_delete_shop_unit(self):
        self.login_owner()
        shop_unit = Unit.objects.create(shop=self.shop, name="皿", unit_type=Unit.UnitType.COUNT)

        response = self.client.delete(reverse("unit-detail", args=[shop_unit.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        shop_unit.refresh_from_db()
        self.assertFalse(shop_unit.is_active)

    def test_staff_cannot_delete_unit(self):
        self.login_staff()
        shop_unit = Unit.objects.create(shop=self.shop, name="皿", unit_type=Unit.UnitType.COUNT)

        response = self.client.delete(reverse("unit-detail", args=[shop_unit.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        shop_unit.refresh_from_db()
        self.assertTrue(shop_unit.is_active)
