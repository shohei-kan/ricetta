# pyright: reportAttributeAccessIssue=false

from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from api.models import Ingredient, PrepTask, Recipe, RecipeIngredient, Unit

from .base import ApiTestCase


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
        self.assertEqual(recipe.recipe_type, Recipe.RecipeType.PREP)
        self.assertEqual(response.data["recipe_type"], "prep")
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(recipe.steps.count(), 1)
        self.assertEqual(response.data["ingredients"][0]["ingredient"]["name"], "玉ねぎ")
        self.assertNotIn("cost", response.data["ingredients"][0])
        self.assertIn("cost_summary", response.data)

    @override_settings(DEMO_MODE=True)
    def test_demo_mode_allows_owner_recipe_create(self):
        self.login_owner()

        response = self.client.post(
            reverse("recipe-list"),
            self.recipe_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Recipe.objects.filter(shop=self.shop, name="トマトソース").exists())

    def test_create_recipe_accepts_recipe_type(self):
        self.login_owner()
        payload = self.recipe_payload()
        payload["recipe_type"] = "menu"

        response = self.client.post(
            reverse("recipe-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data["id"])
        self.assertEqual(recipe.recipe_type, Recipe.RecipeType.MENU)
        self.assertEqual(response.data["recipe_type"], "menu")

    def test_invalid_recipe_type_is_rejected(self):
        self.login_owner()
        payload = self.recipe_payload()
        payload["recipe_type"] = "invalid"

        response = self.client.post(
            reverse("recipe-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recipe_type", response.data)

    def test_staff_can_view_recipes(self):
        self.login_staff()
        unit = self.create_standard_unit("バッチ", Unit.UnitType.CUSTOM)
        recipe = self.create_recipe("トマトソース", unit=unit)
        recipe.recipe_type = Recipe.RecipeType.MENU
        recipe.save()

        list_response = self.client.get(reverse("recipe-list"))
        detail_response = self.client.get(reverse("recipe-detail", args=[recipe.id]))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in list_response.data], ["トマトソース"])
        self.assertEqual(list_response.data[0]["recipe_type"], "menu")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["name"], "トマトソース")
        self.assertEqual(detail_response.data["recipe_type"], "menu")

    def test_staff_cannot_create_recipe(self):
        self.login_staff()

        response = self.client.post(
            reverse("recipe-list"),
            self.recipe_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Recipe.objects.filter(shop=self.shop, name="トマトソース").exists())

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

    def test_staff_cannot_update_recipe(self):
        self.login_staff()
        recipe = self.create_recipe()

        response = self.client.patch(
            reverse("recipe-detail", args=[recipe.id]),
            {"name": "更新できない"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "トマトソース")

    def test_staff_cannot_delete_recipe(self):
        self.login_staff()
        recipe = self.create_recipe()

        response = self.client.delete(reverse("recipe-detail", args=[recipe.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        recipe.refresh_from_db()
        self.assertTrue(recipe.is_active)

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

    def test_menu_cost_summary_uses_material_cost_per_base_yield_unit(self):
        self.login_owner()
        piece = self.create_standard_unit("食分", Unit.UnitType.COUNT)
        ingredient = self.create_ingredient(
            name="惣菜材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=piece,
            purchase_unit=piece,
            purchase_quantity="1",
            purchase_price="100",
        )
        payload = self.recipe_payload(ingredient=ingredient, ingredient_unit=piece)
        payload["recipe_type"] = Recipe.RecipeType.MENU
        payload["base_yield_quantity"] = "10"
        payload["base_yield_unit_id"] = piece.id
        payload["ingredients"][0]["quantity"] = "20"
        payload["selling_price"] = "800"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "200")
        self.assertEqual(response.data["cost_summary"]["gross_profit"], "600")
        self.assertEqual(response.data["cost_summary"]["cost_rate"], "25.00")

    def test_prep_cost_summary_keeps_cost_when_base_yield_quantity_is_one(self):
        self.login_owner()
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)
        ingredient = self.create_ingredient(
            name="ソース材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=gram,
            purchase_unit=gram,
            purchase_quantity="1000",
            purchase_price="500",
        )
        payload = self.recipe_payload(ingredient=ingredient, ingredient_unit=gram)
        payload["recipe_type"] = Recipe.RecipeType.PREP
        payload["base_yield_quantity"] = "1"
        payload["base_yield_unit_id"] = gram.id
        payload["ingredients"][0]["quantity"] = "1000"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "500")

    def test_prep_cost_summary_divides_multiple_base_yield_units(self):
        self.login_owner()
        kilogram = self.create_standard_unit("kg", Unit.UnitType.WEIGHT)
        ingredient = self.create_ingredient(
            name="ソース材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=kilogram,
            purchase_unit=kilogram,
            purchase_quantity="1",
            purchase_price="500",
        )
        payload = self.recipe_payload(ingredient=ingredient, ingredient_unit=kilogram)
        payload["recipe_type"] = Recipe.RecipeType.PREP
        payload["base_yield_quantity"] = "2"
        payload["base_yield_unit_id"] = kilogram.id
        payload["ingredients"][0]["quantity"] = "2"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "500")

    def test_cost_summary_uses_prep_recipe_ingredient_with_kg_to_g_conversion(self):
        self.login_owner()
        gram = self.create_standard_unit("g", Unit.UnitType.WEIGHT)
        kilogram = self.create_standard_unit("kg", Unit.UnitType.WEIGHT)
        meal = self.create_standard_unit("食分", Unit.UnitType.COUNT)
        tomato = self.create_ingredient(
            name="トマト材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=kilogram,
            purchase_unit=kilogram,
            purchase_quantity="1",
            purchase_price="800",
        )
        source_recipe = Recipe.objects.create(
            shop=self.shop,
            name="トマトソース",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="2.5",
            base_yield_unit=kilogram,
        )
        RecipeIngredient.objects.create(
            recipe=source_recipe,
            ingredient=tomato,
            quantity="2.5",
            unit=kilogram,
        )
        tomato_sauce = self.create_ingredient(
            name="トマトソース",
            ingredient_type=Ingredient.IngredientType.PREP_RECIPE,
            source_recipe=source_recipe,
            usage_unit=gram,
        )
        payload = self.recipe_payload(
            base_unit=meal,
            ingredient=tomato_sauce,
            ingredient_unit=gram,
        )
        payload["name"] = "トマトソースパスタ"
        payload["recipe_type"] = Recipe.RecipeType.MENU
        payload["base_yield_quantity"] = "1"
        payload["base_yield_unit_id"] = meal.id
        payload["ingredients"][0]["quantity"] = "150"
        payload["selling_price"] = "1200"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "120")
        self.assertEqual(response.data["cost_summary"]["gross_profit"], "1080")
        self.assertEqual(response.data["cost_summary"]["cost_rate"], "10.00")

    def test_cost_summary_uses_prep_recipe_ingredient_with_l_to_ml_conversion(self):
        self.login_owner()
        liter = self.create_standard_unit("L", Unit.UnitType.VOLUME)
        milliliter = self.create_standard_unit("ml", Unit.UnitType.VOLUME)
        dressing_base = self.create_ingredient(
            name="ドレッシング材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=liter,
            purchase_unit=liter,
            purchase_quantity="1",
            purchase_price="600",
        )
        source_recipe = Recipe.objects.create(
            shop=self.shop,
            name="ドレッシング",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="1",
            base_yield_unit=liter,
        )
        RecipeIngredient.objects.create(
            recipe=source_recipe,
            ingredient=dressing_base,
            quantity="1",
            unit=liter,
        )
        dressing = self.create_ingredient(
            name="ドレッシング",
            ingredient_type=Ingredient.IngredientType.PREP_RECIPE,
            source_recipe=source_recipe,
            usage_unit=milliliter,
        )
        payload = self.recipe_payload(ingredient=dressing, ingredient_unit=milliliter)
        payload["ingredients"][0]["quantity"] = "100"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "60")

    def test_prep_recipe_ingredient_with_unconvertible_unit_costs_zero(self):
        self.login_owner()
        kilogram = self.create_standard_unit("kg", Unit.UnitType.WEIGHT)
        piece = self.create_standard_unit("個", Unit.UnitType.COUNT)
        source_material = self.create_ingredient(
            name="ソース材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=kilogram,
            purchase_unit=kilogram,
            purchase_quantity="1",
            purchase_price="800",
        )
        source_recipe = Recipe.objects.create(
            shop=self.shop,
            name="ソース",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="1",
            base_yield_unit=kilogram,
        )
        RecipeIngredient.objects.create(
            recipe=source_recipe,
            ingredient=source_material,
            quantity="1",
            unit=kilogram,
        )
        sauce = self.create_ingredient(
            name="ソース由来材料",
            ingredient_type=Ingredient.IngredientType.PREP_RECIPE,
            source_recipe=source_recipe,
            usage_unit=piece,
        )
        payload = self.recipe_payload(ingredient=sauce, ingredient_unit=piece)
        payload["ingredients"][0]["quantity"] = "1"

        response = self.client.post(reverse("recipe-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "0")

    def test_recipe_rejects_direct_self_source_recipe_ingredient(self):
        self.login_owner()
        kilogram = self.create_standard_unit("kg", Unit.UnitType.WEIGHT)
        recipe = Recipe.objects.create(
            shop=self.shop,
            name="自己参照レシピ",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="1",
            base_yield_unit=kilogram,
        )
        self_link = self.create_ingredient(
            name="自己参照材料",
            ingredient_type=Ingredient.IngredientType.PREP_RECIPE,
            source_recipe=recipe,
            usage_unit=kilogram,
        )

        response = self.client.patch(
            reverse("recipe-detail", args=[recipe.id]),
            {
                "ingredients": [
                    {
                        "ingredient_id": self_link.id,
                        "quantity": "1",
                        "unit_id": kilogram.id,
                        "sort_order": 1,
                        "memo": "",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ingredients", response.data)

    def test_deep_cycle_cost_summary_does_not_recurse_forever(self):
        self.login_owner()
        kilogram = self.create_standard_unit("kg", Unit.UnitType.WEIGHT)
        recipe_a = Recipe.objects.create(
            shop=self.shop,
            name="レシピA",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="1",
            base_yield_unit=kilogram,
        )
        recipe_b = Recipe.objects.create(
            shop=self.shop,
            name="レシピB",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="1",
            base_yield_unit=kilogram,
        )
        ingredient_a = self.create_ingredient(
            name="レシピA由来",
            ingredient_type=Ingredient.IngredientType.PREP_RECIPE,
            source_recipe=recipe_a,
            usage_unit=kilogram,
        )
        ingredient_b = self.create_ingredient(
            name="レシピB由来",
            ingredient_type=Ingredient.IngredientType.PREP_RECIPE,
            source_recipe=recipe_b,
            usage_unit=kilogram,
        )
        RecipeIngredient.objects.create(
            recipe=recipe_a,
            ingredient=ingredient_b,
            quantity="1",
            unit=kilogram,
        )
        RecipeIngredient.objects.create(
            recipe=recipe_b,
            ingredient=ingredient_a,
            quantity="1",
            unit=kilogram,
        )

        response = self.client.get(reverse("recipe-detail", args=[recipe_a.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "0")

    def test_cost_summary_does_not_divide_by_zero_base_yield_quantity(self):
        self.login_owner()
        kilogram = self.create_standard_unit("kg", Unit.UnitType.WEIGHT)
        ingredient = self.create_ingredient(
            name="ソース材料",
            cost_mode=Ingredient.CostMode.SAME_UNIT,
            usage_unit=kilogram,
            purchase_unit=kilogram,
            purchase_quantity="1",
            purchase_price="500",
        )
        recipe = Recipe.objects.create(
            shop=self.shop,
            name="ゼロ出来上がり量",
            recipe_type=Recipe.RecipeType.PREP,
            base_yield_quantity="0",
            base_yield_unit=kilogram,
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            quantity="2",
            unit=kilogram,
        )

        response = self.client.get(reverse("recipe-detail", args=[recipe.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cost_summary"]["material_cost"], "1000")

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
