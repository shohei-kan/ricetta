# pyright: reportAttributeAccessIssue=false

from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from api.models import (
    BoardMemo,
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

        tomato = Recipe.objects.get(shop=shop, name="トマトソース")
        pickles = Recipe.objects.get(shop=shop, name="ピクルス")
        caponata = Recipe.objects.get(shop=shop, name="カポナータ")
        creme_brulee = Recipe.objects.get(shop=shop, name="クレームブリュレ")
        self.assertEqual(tomato.recipe_type, Recipe.RecipeType.PREP)
        self.assertEqual(tomato.base_yield_quantity, Decimal("2.5"))
        self.assertEqual(tomato.base_yield_unit.name, "kg")
        self.assertEqual(pickles.recipe_type, Recipe.RecipeType.MENU)
        self.assertEqual(pickles.base_yield_quantity, Decimal("10"))
        self.assertEqual(pickles.base_yield_unit.name, "食分")
        self.assertEqual(caponata.ingredients.count(), 12)
        self.assertEqual(caponata.steps.count(), 6)
        self.assertEqual(caponata.recipe_type, Recipe.RecipeType.MENU)
        self.assertEqual(caponata.base_yield_quantity, Decimal("8"))
        self.assertEqual(caponata.base_yield_unit.name, "食分")
        self.assertIsNotNone(caponata.selling_price)
        self.assertEqual(creme_brulee.recipe_type, Recipe.RecipeType.MENU)
        self.assertEqual(creme_brulee.base_yield_quantity, Decimal("6"))
        self.assertEqual(creme_brulee.base_yield_unit.name, "個")
        self.assertFalse(
            Recipe.objects.filter(
                shop=shop,
                name="ベーコンとナスのトマトソースパスタ",
            ).exists()
        )
        self.assertEqual(
            {
                recipe.name: recipe.recipe_type
                for recipe in Recipe.objects.filter(shop=shop)
            },
            {
                "トマトソース": Recipe.RecipeType.PREP,
                "ピクルス": Recipe.RecipeType.MENU,
                "カポナータ": Recipe.RecipeType.MENU,
                "クレームブリュレ": Recipe.RecipeType.MENU,
            },
        )
        tomato_sauce_ingredient = Ingredient.objects.get(shop=shop, name="トマトソース")
        self.assertEqual(
            tomato_sauce_ingredient.ingredient_type,
            Ingredient.IngredientType.PREP_RECIPE,
        )
        self.assertEqual(tomato_sauce_ingredient.source_recipe, tomato)
        self.assertEqual(tomato_sauce_ingredient.usage_unit.name, "g")
        self.assertTrue(
            caponata.ingredients.filter(
                ingredient=tomato_sauce_ingredient,
                quantity=Decimal("600"),
                unit__name="g",
                memo="仕込み済みのトマトソースを使用",
            ).exists()
        )

        prep_statuses = {
            task.recipe.name: task.status
            for task in PrepTask.objects.filter(shop=shop).select_related("recipe")
        }
        self.assertEqual(prep_statuses["トマトソース"], PrepTask.Status.DOING)
        self.assertEqual(prep_statuses["ピクルス"], PrepTask.Status.TODO)
        self.assertEqual(prep_statuses["カポナータ"], PrepTask.Status.TODO)
        self.assertEqual(prep_statuses["クレームブリュレ"], PrepTask.Status.DONE)
        self.assertEqual(
            list(BoardMemo.objects.filter(shop=shop).values_list("text", flat=True)),
            ["玉ねぎ", "ラップ", "フライヤー油交換"],
        )

        first_counts = {
            "users": User.objects.count(),
            "memberships": Membership.objects.count(),
            "recipes": Recipe.objects.count(),
            "recipe_ingredients": RecipeIngredient.objects.count(),
            "recipe_steps": RecipeStep.objects.count(),
            "prep_tasks": PrepTask.objects.count(),
            "board_memos": BoardMemo.objects.count(),
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
        self.assertEqual(BoardMemo.objects.count(), first_counts["board_memos"])

    def test_seed_portfolio_data_reset_recreates_demo_shop_without_touching_other_shop(self):
        call_command("seed_portfolio_data", stdout=StringIO())

        User = get_user_model()
        demo_shop = Shop.objects.get(name="〇〇食堂")
        demo_recipe = Recipe.objects.get(shop=demo_shop, name="カポナータ")
        batch_unit = Unit.objects.get(shop=None, name="バッチ")
        g_unit = Unit.objects.get(shop=None, name="g")
        demo_extra_task = PrepTask.objects.create(
            shop=demo_shop,
            date=timezone.localdate() - timedelta(days=1),
            recipe=demo_recipe,
            planned_quantity=Decimal("99"),
            planned_unit=batch_unit,
            status=PrepTask.Status.TODO,
            memo="resetで消えるデモ作業",
        )
        BoardMemo.objects.create(shop=demo_shop, text="resetで消えるデモメモ")
        Ingredient.objects.create(shop=demo_shop, name="resetで消える材料")

        other_owner = User.objects.create_user(
            username="other-seed@example.com",
            email="other-seed@example.com",
            password="password",
        )
        other_shop = Shop.objects.create(name="別デモではない店舗")
        Membership.objects.create(
            user=other_owner,
            shop=other_shop,
            role=Membership.Role.OWNER,
            display_name="別店舗オーナー",
        )
        other_category = Category.objects.create(shop=other_shop, name="他店舗カテゴリ")
        other_ingredient = Ingredient.objects.create(shop=other_shop, name="他店舗材料")
        other_recipe = Recipe.objects.create(
            shop=other_shop,
            name="他店舗レシピ",
            category=other_category,
            description="他店舗データ",
            base_yield_quantity=Decimal("1"),
            base_yield_unit=g_unit,
            selling_price=Decimal("100"),
            created_by=other_owner,
            updated_by=other_owner,
        )
        other_task = PrepTask.objects.create(
            shop=other_shop,
            date=timezone.localdate(),
            recipe=other_recipe,
            planned_quantity=Decimal("1"),
            planned_unit=g_unit,
            status=PrepTask.Status.TODO,
        )
        other_memo = BoardMemo.objects.create(shop=other_shop, text="他店舗メモ")

        call_command("seed_portfolio_data", "--reset", stdout=StringIO())
        call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        owner = User.objects.get(username="owner@example.com")
        staff = User.objects.get(username="staff@example.com")
        recreated_shop = Shop.objects.get(name="〇〇食堂")
        self.assertTrue(owner.check_password("password"))
        self.assertTrue(staff.check_password("password"))
        self.assertEqual(
            Membership.objects.get(user=owner, shop=recreated_shop).role,
            Membership.Role.OWNER,
        )
        self.assertEqual(
            Membership.objects.get(user=staff, shop=recreated_shop).role,
            Membership.Role.STAFF,
        )

        self.assertFalse(PrepTask.objects.filter(id=demo_extra_task.id).exists())
        self.assertFalse(
            Ingredient.objects.filter(shop=recreated_shop, name="resetで消える材料").exists()
        )
        self.assertEqual(
            Recipe.objects.filter(shop=recreated_shop, is_active=True).count(),
            4,
        )
        self.assertEqual(
            Ingredient.objects.filter(shop=recreated_shop, is_active=True).count(),
            21,
        )
        self.assertEqual(PrepTask.objects.filter(shop=recreated_shop).count(), 4)
        self.assertEqual(
            list(
                BoardMemo.objects.filter(shop=recreated_shop).values_list(
                    "text",
                    flat=True,
                )
            ),
            ["玉ねぎ", "ラップ", "フライヤー油交換"],
        )

        self.assertTrue(Shop.objects.filter(id=other_shop.id).exists())
        self.assertTrue(Ingredient.objects.filter(id=other_ingredient.id).exists())
        self.assertTrue(Recipe.objects.filter(id=other_recipe.id).exists())
        self.assertTrue(PrepTask.objects.filter(id=other_task.id).exists())
        self.assertTrue(BoardMemo.objects.filter(id=other_memo.id).exists())

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
            21,
        )
