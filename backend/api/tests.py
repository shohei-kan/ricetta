# pyright: reportAttributeAccessIssue=false

from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import (
    Category,
    Ingredient,
    Membership,
    PrepTask,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    Shop,
    Unit,
)
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

    def create_category(self, name="仕込み", shop=None):
        return Category.objects.create(shop=shop or self.shop, name=name)

    def create_ingredient(
        self,
        name="卵",
        shop=None,
        cost_mode=Ingredient.CostMode.NONE,
        usage_unit=None,
        purchase_unit=None,
        purchase_quantity=None,
        purchase_price=None,
        conversion_from_quantity=None,
        conversion_from_unit=None,
        conversion_to_quantity=None,
        conversion_to_unit=None,
    ):
        return Ingredient.objects.create(
            shop=shop or self.shop,
            name=name,
            cost_mode=cost_mode,
            usage_unit=usage_unit,
            purchase_unit=purchase_unit,
            purchase_quantity=purchase_quantity,
            purchase_price=purchase_price,
            conversion_from_quantity=conversion_from_quantity,
            conversion_from_unit=conversion_from_unit,
            conversion_to_quantity=conversion_to_quantity,
            conversion_to_unit=conversion_to_unit,
        )

    def create_recipe(self, name="トマトソース", shop=None, unit=None, category=None):
        recipe_shop = shop or self.shop
        return Recipe.objects.create(
            shop=recipe_shop,
            name=name,
            category=category,
            base_yield_quantity="1",
            base_yield_unit=unit or self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM),
        )

    def create_prep_task(
        self,
        recipe=None,
        shop=None,
        unit=None,
        date=None,
        status=PrepTask.Status.TODO,
        sort_order=0,
    ):
        task_shop = shop or self.shop
        task_unit = unit or self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        task_recipe = recipe or self.create_recipe(
            name=f"トマトソース{Recipe.objects.count() + 1}",
            shop=task_shop,
            unit=task_unit,
        )
        return PrepTask.objects.create(
            shop=task_shop,
            date=date or timezone.localdate(),
            recipe=task_recipe,
            planned_quantity="3",
            planned_unit=task_unit,
            status=status,
            sort_order=sort_order,
            completed_at=timezone.now() if status == PrepTask.Status.DONE else None,
        )


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


class RecipeApiTests(ApiTestCase):
    def recipe_payload(self, category=None, base_unit=None, ingredient=None, ingredient_unit=None):
        category = category or self.create_category()
        base_unit = base_unit or self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        ingredient_unit = ingredient_unit or self.create_standard_unit("g", Unit.UnitType.WEIGHT)
        ingredient = ingredient or self.create_ingredient(
            name="玉ねぎ",
            cost_mode=Ingredient.CostMode.NONE,
            usage_unit=ingredient_unit,
        )
        return {
            "name": "トマトソース",
            "category_id": category.id,
            "description": "基本のソース",
            "main_image": None,
            "base_yield_quantity": "1",
            "base_yield_unit_id": base_unit.id,
            "selling_price": None,
            "notes": "焦げないように混ぜる",
            "allergen_notes": "なし",
            "ingredients": [
                {
                    "ingredient_id": ingredient.id,
                    "quantity": "300",
                    "unit_id": ingredient_unit.id,
                    "sort_order": 1,
                    "memo": "",
                }
            ],
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "玉ねぎをみじん切りにする。",
                    "image": None,
                    "memo": "",
                }
            ],
        }

    def test_create_recipe_with_ingredients_and_steps(self):
        self.login_owner()

        response = self.client.post(
            reverse("recipe-list"),
            self.recipe_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data["id"])
        self.assertEqual(recipe.shop, self.shop)
        self.assertEqual(recipe.created_by, self.owner)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(recipe.steps.count(), 1)
        self.assertEqual(response.data["ingredients"][0]["ingredient"]["name"], "玉ねぎ")
        self.assertNotIn("cost", response.data["ingredients"][0])
        self.assertIn("cost_summary", response.data)

    def test_recipe_requires_name(self):
        self.login_owner()
        payload = self.recipe_payload()
        payload.pop("name")

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_base_yield_quantity_must_be_positive(self):
        self.login_owner()
        payload = self.recipe_payload()
        payload["base_yield_quantity"] = "0"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("base_yield_quantity", response.data)

    def test_recipe_requires_base_yield_unit(self):
        self.login_owner()
        payload = self.recipe_payload()
        payload.pop("base_yield_unit_id")

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("base_yield_unit_id", response.data)

    def test_other_shop_category_is_rejected(self):
        self.login_owner()
        other_category = self.create_category("秘密カテゴリ", shop=self.other_shop)
        payload = self.recipe_payload()
        payload["category_id"] = other_category.id

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category_id", response.data)

    def test_other_shop_base_yield_unit_is_rejected(self):
        self.login_owner()
        other_unit = self.create_other_shop_unit("箱", Unit.UnitType.COUNT)
        payload = self.recipe_payload()
        payload["base_yield_unit_id"] = other_unit.id

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("base_yield_unit_id", response.data)

    def test_other_shop_ingredient_is_rejected(self):
        self.login_owner()
        other_ingredient = self.create_ingredient(
            name="秘密材料",
            shop=self.other_shop,
            cost_mode=Ingredient.CostMode.NONE,
        )
        payload = self.recipe_payload()
        payload["ingredients"][0]["ingredient_id"] = other_ingredient.id

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ingredient_id", response.data["ingredients"][0])

    def test_other_shop_recipe_ingredient_unit_is_rejected(self):
        self.login_owner()
        other_unit = self.create_other_shop_unit("箱", Unit.UnitType.COUNT)
        payload = self.recipe_payload()
        payload["ingredients"][0]["unit_id"] = other_unit.id

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unit_id", response.data["ingredients"][0])

    def test_recipe_ingredient_quantity_must_be_positive(self):
        self.login_owner()
        payload = self.recipe_payload()
        payload["ingredients"][0]["quantity"] = "0"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data["ingredients"][0])

    def test_recipe_list_is_scoped_to_current_shop(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        self.create_recipe("自店レシピ", unit=unit)
        self.create_recipe("別店舗レシピ", shop=self.other_shop, unit=unit)

        response = self.client.get(reverse("recipe-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data], ["自店レシピ"])

    def test_recipe_list_supports_query_and_category_filter(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        sauce = self.create_category("ソース")
        dessert = self.create_category("デザート")
        self.create_recipe("トマトソース", unit=unit, category=sauce)
        self.create_recipe("プリン", unit=unit, category=dessert)

        response = self.client.get(
            reverse("recipe-list"),
            {"q": "トマト", "category": sauce.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data], ["トマトソース"])

    def test_cannot_access_other_shop_recipe_detail(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipe = self.create_recipe("秘密レシピ", shop=self.other_shop, unit=unit)

        response = self.client.get(reverse("recipe-detail", args=[recipe.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_shop_recipe(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipe = self.create_recipe("秘密レシピ", shop=self.other_shop, unit=unit)

        response = self.client.patch(
            reverse("recipe-detail", args=[recipe.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "秘密レシピ")

    def test_cannot_delete_other_shop_recipe(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipe = self.create_recipe("秘密レシピ", shop=self.other_shop, unit=unit)

        response = self.client.delete(reverse("recipe-detail", args=[recipe.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        recipe.refresh_from_db()
        self.assertTrue(recipe.is_active)

    def test_delete_marks_inactive_and_hides_from_list(self):
        self.login_owner()
        recipe = self.create_recipe()

        delete_response = self.client.delete(reverse("recipe-detail", args=[recipe.id]))
        list_response = self.client.get(reverse("recipe-list"))

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        recipe.refresh_from_db()
        self.assertFalse(recipe.is_active)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data, [])

    def test_cost_summary_excludes_none_cost_mode(self):
        self.login_owner()

        response = self.client.post(
            reverse("recipe-list"),
            self.recipe_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "0")

    def test_cost_summary_calculates_same_unit(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)
        egg = self.create_ingredient(
            name="卵",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=piece,
            purchase_unit=piece,
            purchase_quantity="1",
            purchase_price="30",
        )
        payload = self.recipe_payload(ingredient=egg, ingredient_unit=piece)
        payload["ingredients"][0]["quantity"] = "3"
        payload["selling_price"] = "120"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "90")
        self.assertEqual(response.data["cost_summary"]["cost_rate"], "75.00")
        self.assertEqual(response.data["cost_summary"]["gross_profit"], "30")

    def test_cost_summary_calculates_conversion(self):
        self.login_owner()
        can = self.create_standard_unit("缶", Unit.UnitType.COUNT)
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)
        tomato = self.create_ingredient(
            name="ホールトマト",
            cost_mode=Ingredient.CostMode.CONVERSION,
            usage_unit=gram,
            purchase_unit=can,
            purchase_quantity="1",
            purchase_price="180",
            conversion_from_quantity="1",
            conversion_from_unit=can,
            conversion_to_quantity="400",
            conversion_to_unit=gram,
        )
        payload = self.recipe_payload(ingredient=tomato, ingredient_unit=gram)
        payload["ingredients"][0]["quantity"] = "200"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "90")
        self.assertIsNone(response.data["cost_summary"]["selling_price"])
        self.assertIsNone(response.data["cost_summary"]["cost_rate"])
        self.assertIsNone(response.data["cost_summary"]["gross_profit"])

    def test_cost_unit_mismatch_is_rejected_for_costed_ingredient(self):
        self.login_owner()
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)
        egg = self.create_ingredient(
            name="卵",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=piece,
            purchase_unit=piece,
            purchase_quantity="1",
            purchase_price="30",
        )
        payload = self.recipe_payload(ingredient=egg, ingredient_unit=gram)

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unit_id", response.data["ingredients"][0])

    def test_patch_replaces_ingredients_and_steps(self):
        self.login_owner()
        create_response = self.client.post(
            reverse("recipe-list"),
            self.recipe_payload(),
            format="json",
        )
        recipe_id = create_response.data["id"]
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)
        egg = self.create_ingredient(
            name="卵",
            cost_mode=Ingredient.CostMode.NONE,
            usage_unit=piece,
        )

        response = self.client.patch(
            reverse("recipe-detail", args=[recipe_id]),
            {
                "ingredients": [
                    {
                        "ingredient_id": egg.id,
                        "quantity": "2",
                        "unit_id": piece.id,
                        "sort_order": 1,
                        "memo": "常温に戻す",
                    }
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "instruction": "卵を割る。",
                        "image": None,
                        "memo": "",
                    },
                    {
                        "step_number": 2,
                        "instruction": "混ぜる。",
                        "image": None,
                        "memo": "",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe = Recipe.objects.get(id=recipe_id)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(recipe.steps.count(), 2)
        self.assertEqual(response.data["ingredients"][0]["ingredient"]["name"], "卵")


class PrepTaskApiTests(ApiTestCase):
    def prep_task_payload(self, recipe=None, unit=None, date=None):
        unit = unit or self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipe = recipe or self.create_recipe(unit=unit)
        return {
            "date": (date or timezone.localdate()).isoformat(),
            "recipe_id": recipe.id,
            "planned_quantity": "3",
            "planned_unit_id": unit.id,
            "memo": "",
            "sort_order": 1,
        }

    def test_create_prep_task_sets_current_shop_and_default_status(self):
        self.login_owner()

        response = self.client.post(
            reverse("prep-task-list"),
            {**self.prep_task_payload(), "shop": self.other_shop.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = PrepTask.objects.get(id=response.data["id"])
        self.assertEqual(task.shop, self.shop)
        self.assertEqual(task.status, PrepTask.Status.TODO)
        self.assertEqual(response.data["status"], "todo")

    def test_planned_quantity_must_be_positive(self):
        self.login_owner()
        payload = self.prep_task_payload()
        payload["planned_quantity"] = "0"

        response = self.client.post(reverse("prep-task-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("planned_quantity", response.data)

    def test_date_is_required(self):
        self.login_owner()
        payload = self.prep_task_payload()
        payload.pop("date")

        response = self.client.post(reverse("prep-task-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_recipe_is_required(self):
        self.login_owner()
        payload = self.prep_task_payload()
        payload.pop("recipe_id")

        response = self.client.post(reverse("prep-task-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recipe_id", response.data)

    def test_planned_unit_is_required(self):
        self.login_owner()
        payload = self.prep_task_payload()
        payload.pop("planned_unit_id")

        response = self.client.post(reverse("prep-task-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("planned_unit_id", response.data)

    def test_other_shop_recipe_is_rejected(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        other_recipe = self.create_recipe("秘密レシピ", shop=self.other_shop, unit=unit)
        payload = self.prep_task_payload(recipe=other_recipe, unit=unit)

        response = self.client.post(reverse("prep-task-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recipe_id", response.data)

    def test_other_shop_unit_is_rejected(self):
        self.login_owner()
        other_unit = self.create_other_shop_unit("箱", Unit.UnitType.COUNT)
        payload = self.prep_task_payload()
        payload["planned_unit_id"] = other_unit.id

        response = self.client.post(reverse("prep-task-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("planned_unit_id", response.data)

    def test_list_is_scoped_to_current_shop(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipe = self.create_recipe("トマトソース", unit=unit)
        self.create_prep_task(recipe=recipe, unit=unit, sort_order=1)
        self.create_prep_task(shop=self.other_shop, unit=unit, sort_order=2)

        response = self.client.get(reverse("prep-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tasks"]), 1)
        self.assertEqual(response.data["tasks"][0]["recipe"]["name"], "トマトソース")

    def test_cannot_access_other_shop_detail(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        task = self.create_prep_task(shop=self.other_shop, unit=unit)

        response = self.client.get(reverse("prep-task-detail", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_shop_prep_task(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        task = self.create_prep_task(shop=self.other_shop, unit=unit)

        response = self.client.patch(
            reverse("prep-task-detail", args=[task.id]),
            {"memo": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        task.refresh_from_db()
        self.assertEqual(task.memo, "")

    def test_cannot_delete_other_shop_prep_task(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        task = self.create_prep_task(shop=self.other_shop, unit=unit)

        response = self.client.delete(reverse("prep-task-detail", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PrepTask.objects.filter(id=task.id).exists())

    def test_list_returns_unfinished_and_today_completed_with_summary(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        today = timezone.localdate()
        past = today - timedelta(days=3)
        self.create_prep_task(unit=unit, date=past, status=PrepTask.Status.TODO, sort_order=2)
        self.create_prep_task(unit=unit, date=past, status=PrepTask.Status.DOING, sort_order=1)
        self.create_prep_task(unit=unit, date=past, status=PrepTask.Status.DONE, sort_order=3)
        old_done = self.create_prep_task(
            unit=unit,
            date=past,
            status=PrepTask.Status.DONE,
            sort_order=4,
        )
        PrepTask.objects.filter(id=old_done.id).update(
            completed_at=timezone.now() - timedelta(days=2)
        )

        response = self.client.get(reverse("prep-task-list"), {"date": today.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["date"], today.isoformat())
        self.assertEqual(response.data["summary"], {"todo": 1, "doing": 1, "done": 1})
        self.assertEqual(len(response.data["tasks"]), 3)
        self.assertEqual([item["sort_order"] for item in response.data["tasks"]], [1, 2, 3])

    def test_list_includes_past_todo_task(self):
        self.login_owner()
        task = self.create_prep_task(
            date=timezone.localdate() - timedelta(days=7),
            status=PrepTask.Status.TODO,
        )

        response = self.client.get(reverse("prep-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(task.id, [item["id"] for item in response.data["tasks"]])

    def test_list_includes_past_doing_task(self):
        self.login_owner()
        task = self.create_prep_task(
            date=timezone.localdate() - timedelta(days=7),
            status=PrepTask.Status.DOING,
        )

        response = self.client.get(reverse("prep-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(task.id, [item["id"] for item in response.data["tasks"]])

    def test_list_includes_done_task_completed_today(self):
        self.login_owner()
        task = self.create_prep_task(
            date=timezone.localdate() - timedelta(days=7),
            status=PrepTask.Status.DONE,
        )

        response = self.client.get(reverse("prep-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(task.id, [item["id"] for item in response.data["tasks"]])

    def test_list_excludes_done_task_completed_before_today(self):
        self.login_owner()
        task = self.create_prep_task(status=PrepTask.Status.DONE)
        PrepTask.objects.filter(id=task.id).update(
            completed_at=timezone.now() - timedelta(days=2)
        )

        response = self.client.get(reverse("prep-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(task.id, [item["id"] for item in response.data["tasks"]])

    def test_list_uses_today_when_date_is_omitted(self):
        self.login_owner()
        today = timezone.localdate()
        self.create_prep_task(date=today)
        self.create_prep_task(date=today + timedelta(days=1))

        response = self.client.get(reverse("prep-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["date"], today.isoformat())
        self.assertEqual(len(response.data["tasks"]), 2)

    def test_invalid_list_date_returns_error(self):
        self.login_owner()

        response = self.client.get(reverse("prep-task-list"), {"date": "not-a-date"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_update_to_todo_and_doing(self):
        self.login_owner()
        task = self.create_prep_task(status=PrepTask.Status.DONE)

        todo_response = self.client.patch(
            reverse("prep-task-update-status", args=[task.id]),
            {"status": "todo"},
            format="json",
        )
        doing_response = self.client.patch(
            reverse("prep-task-update-status", args=[task.id]),
            {"status": "doing"},
            format="json",
        )

        self.assertEqual(todo_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(todo_response.data["completed_at"])
        self.assertEqual(doing_response.status_code, status.HTTP_200_OK)
        self.assertEqual(doing_response.data["status"], "doing")
        self.assertIsNone(doing_response.data["completed_at"])

    def test_status_update_to_done_sets_completed_at(self):
        self.login_owner()
        task = self.create_prep_task(status=PrepTask.Status.TODO)

        response = self.client.patch(
            reverse("prep-task-update-status", args=[task.id]),
            {"status": "done"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "done")
        self.assertIsNotNone(response.data["completed_at"])

    def test_regular_patch_status_updates_completed_at(self):
        self.login_owner()
        task = self.create_prep_task(status=PrepTask.Status.TODO)

        done_response = self.client.patch(
            reverse("prep-task-detail", args=[task.id]),
            {"status": "done"},
            format="json",
        )
        todo_response = self.client.patch(
            reverse("prep-task-detail", args=[task.id]),
            {"status": "todo"},
            format="json",
        )

        self.assertEqual(done_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(done_response.data["completed_at"])
        self.assertEqual(todo_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(todo_response.data["completed_at"])

    def test_invalid_status_is_rejected(self):
        self.login_owner()
        task = self.create_prep_task()

        response = self.client.patch(
            reverse("prep-task-update-status", args=[task.id]),
            {"status": "blocked"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_cannot_update_other_shop_status(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        task = self.create_prep_task(shop=self.other_shop, unit=unit)

        response = self.client.patch(
            reverse("prep-task-update-status", args=[task.id]),
            {"status": "done"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        task.refresh_from_db()
        self.assertEqual(task.status, PrepTask.Status.TODO)

    def test_delete_prep_task(self):
        self.login_owner()
        task = self.create_prep_task()

        response = self.client.delete(reverse("prep-task-detail", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PrepTask.objects.filter(id=task.id).exists())


class DashboardApiTests(ApiTestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_is_scoped_to_current_shop(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        today = timezone.localdate()
        recipe = Recipe.objects.create(
            shop=self.shop,
            name="自店レシピ",
            base_yield_quantity="1",
            base_yield_unit=unit,
        )
        Recipe.objects.create(
            shop=self.other_shop,
            name="別店舗レシピ",
            base_yield_quantity="1",
            base_yield_unit=unit,
        )
        Ingredient.objects.create(shop=self.shop, name="塩")
        Ingredient.objects.create(shop=self.other_shop, name="秘密材料")
        self.create_prep_task(recipe=recipe, unit=unit, date=today)
        self.create_prep_task(
            recipe=self.create_recipe("別店舗仕込み", shop=self.other_shop, unit=unit),
            shop=self.other_shop,
            unit=unit,
            date=today,
        )

        response = self.client.get(reverse("dashboard"), {"date": today.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stats"]["recipe_count"], 1)
        self.assertEqual(response.data["stats"]["ingredient_count"], 1)
        self.assertEqual(response.data["stats"]["prep_task_count"], 1)
        self.assertEqual(len(response.data["next_tasks"]), 1)

    def test_prep_summary_matches_prep_today_active_task_scope(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        past = today - timedelta(days=3)
        self.create_prep_task(unit=unit, date=past, status=PrepTask.Status.TODO)
        self.create_prep_task(unit=unit, date=past, status=PrepTask.Status.DOING)
        self.create_prep_task(unit=unit, date=today, status=PrepTask.Status.DONE)
        old_done = self.create_prep_task(unit=unit, date=past, status=PrepTask.Status.DONE)
        self.create_prep_task(unit=unit, date=tomorrow, status=PrepTask.Status.TODO)
        PrepTask.objects.filter(id=old_done.id).update(
            completed_at=timezone.now() - timedelta(days=2)
        )

        today_response = self.client.get(reverse("dashboard"), {"date": today.isoformat()})
        tomorrow_response = self.client.get(
            reverse("dashboard"),
            {"date": tomorrow.isoformat()},
        )

        self.assertEqual(today_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            today_response.data["prep_summary"],
            {"todo": 2, "doing": 1, "done": 1},
        )
        self.assertEqual(
            tomorrow_response.data["prep_summary"],
            {"todo": 2, "doing": 1, "done": 0},
        )
        self.assertEqual(today_response.data["stats"]["prep_task_count"], 4)

    def test_dashboard_uses_today_when_date_is_omitted(self):
        self.login_owner()
        today = timezone.localdate()
        self.create_prep_task(date=today)
        self.create_prep_task(date=today + timedelta(days=1))

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["date"], today.isoformat())
        self.assertEqual(response.data["stats"]["prep_task_count"], 2)

    def test_invalid_dashboard_date_returns_error(self):
        self.login_owner()

        response = self.client.get(reverse("dashboard"), {"date": "bad-date"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_next_tasks_prioritizes_doing_then_todo_and_orders_by_sort_order(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        today = timezone.localdate()
        for index in range(6):
            self.create_prep_task(
                recipe=self.create_recipe(name=f"仕込み{index}", unit=unit),
                unit=unit,
                date=today,
                status=PrepTask.Status.TODO,
                sort_order=10 - index,
            )
        self.create_prep_task(
            recipe=self.create_recipe(name="作業中の仕込み", unit=unit),
            unit=unit,
            date=today,
            status=PrepTask.Status.DOING,
            sort_order=99,
        )
        self.create_prep_task(
            recipe=self.create_recipe(name="完了済み", unit=unit),
            unit=unit,
            date=today,
            status=PrepTask.Status.DONE,
            sort_order=0,
        )
        self.create_prep_task(shop=self.other_shop, unit=unit, date=today, sort_order=1)

        response = self.client.get(reverse("dashboard"), {"date": today.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["next_tasks"]), 5)
        self.assertNotIn(
            "完了済み",
            [task["recipe"]["name"] for task in response.data["next_tasks"]],
        )
        self.assertEqual(
            [task["status"] for task in response.data["next_tasks"]],
            ["doing", "todo", "todo", "todo", "todo"],
        )
        self.assertEqual(
            [task["recipe"]["name"] for task in response.data["next_tasks"]],
            ["作業中の仕込み", "仕込み5", "仕込み4", "仕込み3", "仕込み2"],
        )

    def test_frequent_recipes_are_ordered_by_prep_task_usage_and_limited_to_five(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipes = [
            self.create_recipe(name=f"よく使う{i}", unit=unit)
            for i in range(6)
        ]
        for recipe_index, recipe in enumerate(recipes):
            for task_index in range(recipe_index + 1):
                self.create_prep_task(
                    recipe=recipe,
                    unit=unit,
                    sort_order=recipe_index * 10 + task_index,
                )
        other_recipe = self.create_recipe(
            name="別店舗頻出",
            shop=self.other_shop,
            unit=unit,
        )
        for index in range(10):
            self.create_prep_task(
                recipe=other_recipe,
                shop=self.other_shop,
                unit=unit,
                sort_order=index,
            )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["frequent_recipes"]), 5)
        self.assertEqual(response.data["frequent_recipes"][0]["name"], "よく使う5")
        self.assertNotIn(
            "別店舗頻出",
            [recipe["name"] for recipe in response.data["frequent_recipes"]],
        )

    def test_stats_count_active_records_and_alerts_are_empty(self):
        self.login_owner()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        today = timezone.localdate()
        recipe = Recipe.objects.create(
            shop=self.shop,
            name="有効レシピ",
            base_yield_quantity="1",
            base_yield_unit=unit,
        )
        Recipe.objects.create(
            shop=self.shop,
            name="無効レシピ",
            base_yield_quantity="1",
            base_yield_unit=unit,
            is_active=False,
        )
        Ingredient.objects.create(shop=self.shop, name="有効材料")
        Ingredient.objects.create(shop=self.shop, name="無効材料", is_active=False)
        self.create_prep_task(recipe=recipe, unit=unit, date=today)
        self.create_prep_task(recipe=recipe, unit=unit, date=today + timedelta(days=1))

        response = self.client.get(reverse("dashboard"), {"date": today.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stats"]["recipe_count"], 1)
        self.assertEqual(response.data["stats"]["ingredient_count"], 1)
        self.assertEqual(response.data["stats"]["prep_task_count"], 2)
        self.assertEqual(response.data["alerts"], [])


class PortfolioSeedCommandTests(TestCase):
    def test_seed_portfolio_data_creates_demo_records_idempotently(self):
        call_command("seed_portfolio_data", stdout=StringIO())

        User = get_user_model()
        owner = User.objects.get(username="owner@example.com")
        staff = User.objects.get(username="staff@example.com")
        shop = Shop.objects.get(name="〇〇食堂")

        owner_membership = Membership.objects.get(user=owner, shop=shop)
        staff_membership = Membership.objects.get(user=staff, shop=shop)
        self.assertEqual(owner_membership.role, Membership.Role.OWNER)
        self.assertEqual(staff_membership.role, Membership.Role.STAFF)

        self.assertEqual(Category.objects.filter(shop=shop).count(), 4)
        for unit_name in ["g", "kg", "ml", "L", "個", "本", "枚", "食分"]:
            self.assertTrue(Unit.objects.filter(shop=None, name=unit_name).exists())

        caponata = Recipe.objects.get(shop=shop, name="カポナータ")
        self.assertEqual(caponata.ingredients.count(), 12)
        self.assertEqual(caponata.steps.count(), 6)
        self.assertIsNotNone(caponata.selling_price)

        prep_statuses = {
            task.recipe.name: task.status
            for task in PrepTask.objects.filter(shop=shop).select_related("recipe")
        }
        self.assertEqual(prep_statuses["トマトソース"], PrepTask.Status.DOING)
        self.assertEqual(prep_statuses["ピクルス"], PrepTask.Status.TODO)
        self.assertEqual(prep_statuses["カポナータ"], PrepTask.Status.TODO)
        self.assertEqual(prep_statuses["クレームブリュレ"], PrepTask.Status.DONE)

        first_counts = {
            "users": User.objects.count(),
            "memberships": Membership.objects.count(),
            "recipes": Recipe.objects.count(),
            "recipe_ingredients": RecipeIngredient.objects.count(),
            "recipe_steps": RecipeStep.objects.count(),
            "prep_tasks": PrepTask.objects.count(),
        }

        call_command("seed_portfolio_data", stdout=StringIO())

        self.assertEqual(User.objects.count(), first_counts["users"])
        self.assertEqual(Membership.objects.count(), first_counts["memberships"])
        self.assertEqual(Recipe.objects.count(), first_counts["recipes"])
        self.assertEqual(
            RecipeIngredient.objects.count(),
            first_counts["recipe_ingredients"],
        )
        self.assertEqual(RecipeStep.objects.count(), first_counts["recipe_steps"])
        self.assertEqual(PrepTask.objects.count(), first_counts["prep_tasks"])

    def test_seed_portfolio_data_uses_existing_owner_current_shop(self):
        User = get_user_model()
        owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="old-password",
        )
        old_shop = Shop.objects.create(name="bar musica.")
        Membership.objects.create(
            user=owner,
            shop=old_shop,
            role=Membership.Role.OWNER,
            display_name="旧オーナー",
        )

        call_command("seed_portfolio_data", stdout=StringIO())

        current_membership = (
            Membership.objects.select_related("shop")
            .filter(user=owner, is_active=True)
            .order_by("id")
            .first()
        )
        if current_membership is None:
            self.fail("seed_portfolio_data should keep an active owner membership.")

        self.assertEqual(current_membership.shop.name, "〇〇食堂")
        self.assertEqual(current_membership.role, Membership.Role.OWNER)
        self.assertEqual(
            Recipe.objects.filter(shop=current_membership.shop, is_active=True).count(),
            4,
        )
        self.assertEqual(
            Ingredient.objects.filter(
                shop=current_membership.shop,
                is_active=True,
            ).count(),
            20,
        )
