# pyright: reportAttributeAccessIssue=false

from django.urls import reverse
from rest_framework import status

from api.models import Ingredient, Unit

from .base import ApiTestCase


class IngredientApiTests(ApiTestCase):
    def test_create_none_cost_mode(self):
        self.login_owner()

        response = self.client.post(
            reverse("ingredient-list"),
            {"name": "塩少々", "supplier": "", "memo": "", "cost_mode": "none"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ingredient = Ingredient.objects.get(id=response.data["id"])
        self.assertEqual(ingredient.shop, self.shop)
        self.assertEqual(ingredient.cost_mode, Ingredient.CostMode.NONE)
        self.assertIsNone(response.data["unit_cost_label"])

    def test_create_same_unit_cost_mode(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "卵",
                "cost_mode": "same_unit",
                "purchase_quantity": "1",
                "purchase_unit_id": piece.id,
                "purchase_price": "30",
                "usage_unit_id": piece.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["purchase_unit"]["name"], "個")
        self.assertEqual(response.data["usage_unit"]["name"], "個")
        self.assertEqual(response.data["unit_cost_label"], "30円 / 個")

    def test_create_conversion_cost_mode(self):
        self.login_owner()
        can = self.create_standard_unit("缶", Unit.UnitType.COUNT)
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "ホールトマト",
                "supplier": "業務スーパー",
                "cost_mode": "conversion",
                "purchase_quantity": "1",
                "purchase_unit_id": can.id,
                "purchase_price": "180",
                "usage_unit_id": gram.id,
                "conversion_from_quantity": "1",
                "conversion_from_unit_id": can.id,
                "conversion_to_quantity": "400",
                "conversion_to_unit_id": gram.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["conversion"]["from_unit"]["name"], "缶")
        self.assertEqual(response.data["conversion"]["to_unit"]["name"], "g")
        self.assertEqual(response.data["unit_cost_label"], "0.45円 / g")

    def test_same_unit_requires_purchase_quantity(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "卵",
                "cost_mode": "same_unit",
                "purchase_unit_id": piece.id,
                "purchase_price": "30",
                "usage_unit_id": piece.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_quantity", response.data)

    def test_same_unit_requires_purchase_price(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "卵",
                "cost_mode": "same_unit",
                "purchase_quantity": "1",
                "purchase_unit_id": piece.id,
                "usage_unit_id": piece.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_price", response.data)

    def test_conversion_requires_conversion_to_quantity(self):
        self.login_owner()
        can = self.create_standard_unit("缶", Unit.UnitType.COUNT)
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "ホールトマト",
                "cost_mode": "conversion",
                "purchase_quantity": "1",
                "purchase_unit_id": can.id,
                "purchase_price": "180",
                "usage_unit_id": gram.id,
                "conversion_from_quantity": "1",
                "conversion_from_unit_id": can.id,
                "conversion_to_unit_id": gram.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("conversion_to_quantity", response.data)

    def test_quantity_must_be_positive(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "卵",
                "cost_mode": "same_unit",
                "purchase_quantity": "0",
                "purchase_unit_id": piece.id,
                "purchase_price": "30",
                "usage_unit_id": piece.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_quantity", response.data)

    def test_purchase_price_must_be_non_negative(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "卵",
                "cost_mode": "same_unit",
                "purchase_quantity": "1",
                "purchase_unit_id": piece.id,
                "purchase_price": "-1",
                "usage_unit_id": piece.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_price", response.data)

    def test_list_is_scoped_to_current_shop(self):
        self.login_owner()
        Ingredient.objects.create(shop=self.shop, name="塩", cost_mode=Ingredient.CostMode.NONE)
        Ingredient.objects.create(shop=self.other_shop, name="秘密材料", cost_mode=Ingredient.CostMode.NONE)

        response = self.client.get(reverse("ingredient-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data], ["塩"])

    def test_create_sets_current_shop(self):
        self.login_owner()

        response = self.client.post(
            reverse("ingredient-list"),
            {"name": "砂糖", "cost_mode": "none", "shop": self.other_shop.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ingredient = Ingredient.objects.get(id=response.data["id"])
        self.assertEqual(ingredient.shop, self.shop)

    def test_owner_can_update_ingredient(self):
        self.login_owner()
        ingredient = Ingredient.objects.create(
            shop=self.shop,
            name="砂糖",
            cost_mode=Ingredient.CostMode.NONE,
        )

        response = self.client.patch(
            reverse("ingredient-detail", args=[ingredient.id]),
            {"name": "グラニュー糖"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, "グラニュー糖")

    def test_staff_can_view_ingredients(self):
        self.login_staff()
        ingredient = Ingredient.objects.create(
            shop=self.shop,
            name="塩",
            cost_mode=Ingredient.CostMode.NONE,
        )

        list_response = self.client.get(reverse("ingredient-list"))
        detail_response = self.client.get(reverse("ingredient-detail", args=[ingredient.id]))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in list_response.data], ["塩"])
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["name"], "塩")

    def test_staff_cannot_create_ingredient(self):
        self.login_staff()

        response = self.client.post(
            reverse("ingredient-list"),
            {"name": "砂糖", "cost_mode": "none"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Ingredient.objects.filter(shop=self.shop, name="砂糖").exists())

    def test_staff_cannot_update_ingredient(self):
        self.login_staff()
        ingredient = Ingredient.objects.create(
            shop=self.shop,
            name="砂糖",
            cost_mode=Ingredient.CostMode.NONE,
        )

        response = self.client.patch(
            reverse("ingredient-detail", args=[ingredient.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, "砂糖")

    def test_staff_cannot_delete_ingredient(self):
        self.login_staff()
        ingredient = Ingredient.objects.create(
            shop=self.shop,
            name="砂糖",
            cost_mode=Ingredient.CostMode.NONE,
        )

        response = self.client.delete(reverse("ingredient-detail", args=[ingredient.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        ingredient.refresh_from_db()
        self.assertTrue(ingredient.is_active)

    def test_cannot_access_other_shop_detail(self):
        self.login_owner()
        ingredient = Ingredient.objects.create(
            shop=self.other_shop,
            name="秘密材料",
            cost_mode=Ingredient.CostMode.NONE,
        )

        response = self.client.get(reverse("ingredient-detail", args=[ingredient.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_shop_ingredient(self):
        self.login_owner()
        ingredient = Ingredient.objects.create(
            shop=self.other_shop,
            name="秘密材料",
            cost_mode=Ingredient.CostMode.NONE,
        )

        response = self.client.patch(
            reverse("ingredient-detail", args=[ingredient.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, "秘密材料")

    def test_cannot_delete_other_shop_ingredient(self):
        self.login_owner()
        ingredient = Ingredient.objects.create(
            shop=self.other_shop,
            name="秘密材料",
            cost_mode=Ingredient.CostMode.NONE,
        )

        response = self.client.delete(reverse("ingredient-detail", args=[ingredient.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        ingredient.refresh_from_db()
        self.assertTrue(ingredient.is_active)

    def test_can_create_with_standard_unit(self):
        self.login_owner()
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "小麦粉",
                "cost_mode": "same_unit",
                "purchase_quantity": "1000",
                "purchase_unit_id": gram.id,
                "purchase_price": "300",
                "usage_unit_id": gram.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_create_with_current_shop_unit(self):
        self.login_owner()
        plate = self.create_shop_unit("皿", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "盛り合わせ",
                "cost_mode": "same_unit",
                "purchase_quantity": "1",
                "purchase_unit_id": plate.id,
                "purchase_price": "500",
                "usage_unit_id": plate.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_other_shop_unit_is_rejected(self):
        self.login_owner()
        other_unit = self.create_other_shop_unit("箱", Unit.UnitType.COUNT)

        response = self.client.post(
            reverse("ingredient-list"),
            {
                "name": "箱入り材料",
                "cost_mode": "same_unit",
                "purchase_quantity": "1",
                "purchase_unit_id": other_unit.id,
                "purchase_price": "500",
                "usage_unit_id": other_unit.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_unit_id", response.data)

    def test_delete_marks_inactive_and_hides_from_list(self):
        self.login_owner()
        ingredient = Ingredient.objects.create(
            shop=self.shop,
            name="塩",
            cost_mode=Ingredient.CostMode.NONE,
        )

        delete_response = self.client.delete(reverse("ingredient-detail", args=[ingredient.id]))
        list_response = self.client.get(reverse("ingredient-list"))

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        ingredient.refresh_from_db()
        self.assertFalse(ingredient.is_active)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data, [])
