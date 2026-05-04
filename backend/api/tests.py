from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category, Ingredient, Membership, Shop, Unit
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

    def create_standard_unit(self, name="g", unit_type=Unit.UnitType.WEIGHT):
        return Unit.objects.create(
            shop=None,
            name=name,
            unit_type=unit_type,
            is_default=True,
        )

    def create_shop_unit(self, name="個", unit_type=Unit.UnitType.COUNT):
        return Unit.objects.create(
            shop=self.shop,
            name=name,
            unit_type=unit_type,
        )

    def create_other_shop_unit(self, name="箱", unit_type=Unit.UnitType.COUNT):
        return Unit.objects.create(
            shop=self.other_shop,
            name=name,
            unit_type=unit_type,
        )


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
