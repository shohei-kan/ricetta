# pyright: reportAttributeAccessIssue=false

from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
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
    def test_reset_on_fresh_database_creates_demo_shop(self):
        call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        demo_shop = Shop.objects.get(demo_key="portfolio-demo")
        self.assertEqual(demo_shop.name, "〇〇食堂")
        self.assertEqual(demo_shop.memberships.count(), 2)
        self.assertEqual(Recipe.objects.filter(shop=demo_shop).count(), 4)

    def test_seed_portfolio_data_creates_demo_records_idempotently(self):
        call_command("seed_portfolio_data", stdout=StringIO())

        User = get_user_model()
        owner = User.objects.get(username="owner@example.com")
        staff = User.objects.get(username="staff@example.com")
        shop = Shop.objects.get(demo_key="portfolio-demo")
        self.assertEqual(shop.name, "〇〇食堂")

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
        assert tomato_sauce_ingredient.usage_unit is not None
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
        self.assertEqual(Shop.objects.filter(demo_key="portfolio-demo").count(), 1)

    def test_seed_portfolio_data_reset_recreates_demo_shop_without_touching_other_shop(self):
        call_command("seed_portfolio_data", stdout=StringIO())

        User = get_user_model()
        demo_shop = Shop.objects.get(demo_key="portfolio-demo")
        demo_shop_id = demo_shop.id
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
        owner_membership_id = Membership.objects.get(
            user__username="owner@example.com",
            shop=demo_shop,
        ).id
        staff_membership_id = Membership.objects.get(
            user__username="staff@example.com",
            shop=demo_shop,
        ).id

        call_command("seed_portfolio_data", "--reset", stdout=StringIO())
        call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        owner = User.objects.get(username="owner@example.com")
        staff = User.objects.get(username="staff@example.com")
        recreated_shop = Shop.objects.get(demo_key="portfolio-demo")
        self.assertEqual(recreated_shop.id, demo_shop_id)
        self.assertEqual(recreated_shop.name, "〇〇食堂")
        self.assertTrue(owner.check_password("password"))
        self.assertTrue(staff.check_password("password"))
        self.assertTrue(
            self.client.login(username="owner@example.com", password="password")
        )
        self.client.logout()
        self.assertTrue(
            self.client.login(username="staff@example.com", password="password")
        )
        self.client.logout()
        self.assertEqual(
            Membership.objects.get(user=owner, shop=recreated_shop).role,
            Membership.Role.OWNER,
        )
        self.assertEqual(
            Membership.objects.get(user=staff, shop=recreated_shop).role,
            Membership.Role.STAFF,
        )
        self.assertEqual(
            Membership.objects.get(user=owner, shop=recreated_shop).id,
            owner_membership_id,
        )
        self.assertEqual(
            Membership.objects.get(user=staff, shop=recreated_shop).id,
            staff_membership_id,
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
        self.assertEqual(current_membership.shop, old_shop)
        self.assertEqual(current_membership.shop.demo_key, "portfolio-demo")
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

    def test_reset_migrates_unique_existing_owner_membership_shop(self):
        User = get_user_model()
        owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="old-password",
        )
        existing_shop = Shop.objects.create(name="変更済み店舗名")
        Membership.objects.create(
            user=owner,
            shop=existing_shop,
            role=Membership.Role.OWNER,
        )

        call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        existing_shop.refresh_from_db()
        self.assertEqual(existing_shop.demo_key, "portfolio-demo")
        self.assertEqual(existing_shop.name, "〇〇食堂")
        self.assertEqual(Shop.objects.count(), 1)
        self.assertEqual(Recipe.objects.filter(shop=existing_shop).count(), 4)

    def test_ambiguous_owner_memberships_fail_closed_without_changes(self):
        User = get_user_model()
        owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="old-password",
        )
        first_shop = Shop.objects.create(name="候補店舗A")
        second_shop = Shop.objects.create(name="候補店舗B")
        Membership.objects.create(user=owner, shop=first_shop, role=Membership.Role.OWNER)
        Membership.objects.create(user=owner, shop=second_shop, role=Membership.Role.OWNER)

        with self.assertRaisesMessage(CommandError, "expected exactly 1"):
            call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        self.assertEqual(Shop.objects.count(), 2)
        self.assertFalse(Shop.objects.filter(demo_key="portfolio-demo").exists())
        self.assertEqual(
            list(Shop.objects.order_by("id").values_list("name", flat=True)),
            ["候補店舗A", "候補店舗B"],
        )
        self.assertEqual(Membership.objects.count(), 2)

    def test_existing_owner_without_membership_fails_closed(self):
        User = get_user_model()
        User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="old-password",
        )

        with self.assertRaisesMessage(CommandError, "has 0 Membership candidates"):
            call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        self.assertEqual(Shop.objects.count(), 0)
        self.assertEqual(Membership.objects.count(), 0)

    def test_non_owner_or_inactive_membership_fails_closed(self):
        User = get_user_model()
        cases = [
            (Membership.Role.STAFF, True),
            (Membership.Role.OWNER, False),
        ]
        for index, (role, is_active) in enumerate(cases):
            with self.subTest(role=role, is_active=is_active):
                owner = User.objects.create_user(
                    username=f"candidate-{index}@example.com",
                    email=f"candidate-{index}@example.com",
                    password="old-password",
                )
                shop = Shop.objects.create(name=f"候補店舗{index}")
                Membership.objects.create(
                    user=owner,
                    shop=shop,
                    role=role,
                    is_active=is_active,
                )

                with self.assertRaisesMessage(CommandError, "role=owner"):
                    call_command(
                        "seed_portfolio_data",
                        "--reset",
                        owner_email=owner.username,
                        stdout=StringIO(),
                    )

                shop.refresh_from_db()
                self.assertIsNone(shop.demo_key)

    def test_demo_key_and_owner_membership_mismatch_fails_before_reset(self):
        User = get_user_model()
        owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="old-password",
        )
        keyed_shop = Shop.objects.create(
            name="識別子付き店舗",
            demo_key="portfolio-demo",
        )
        owner_shop = Shop.objects.create(name="owner所属店舗")
        Membership.objects.create(
            user=owner,
            shop=owner_shop,
            role=Membership.Role.OWNER,
        )
        marker = Ingredient.objects.create(shop=keyed_shop, name="削除されない材料")

        with self.assertRaisesMessage(CommandError, "point to different Shops"):
            call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        self.assertTrue(Ingredient.objects.filter(id=marker.id).exists())
        self.assertEqual(keyed_shop.memberships.count(), 0)
        self.assertTrue(
            Membership.objects.filter(user=owner, shop=owner_shop).exists()
        )

    def test_demo_key_assignment_and_reset_roll_back_on_late_failure(self):
        User = get_user_model()
        owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="old-password",
        )
        existing_shop = Shop.objects.create(name="既存デモ店舗")
        Membership.objects.create(
            user=owner,
            shop=existing_shop,
            role=Membership.Role.OWNER,
        )
        marker = Ingredient.objects.create(shop=existing_shop, name="rollback対象材料")

        def fail_after_migration_and_reseed(command, shop):
            shop.refresh_from_db()
            self.assertEqual(shop.demo_key, "portfolio-demo")
            self.assertFalse(Ingredient.objects.filter(id=marker.id).exists())
            self.assertEqual(Recipe.objects.filter(shop=shop).count(), 4)
            raise RuntimeError("simulated failure after demo Shop migration")

        with patch(
            "api.management.commands.seed_portfolio_data.Command._seed_board_memos",
            autospec=True,
            side_effect=fail_after_migration_and_reseed,
        ):
            with self.assertRaisesMessage(
                RuntimeError,
                "simulated failure after demo Shop migration",
            ):
                call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        existing_shop.refresh_from_db()
        self.assertIsNone(existing_shop.demo_key)
        self.assertEqual(existing_shop.name, "既存デモ店舗")
        self.assertTrue(Ingredient.objects.filter(id=marker.id).exists())

    def test_reset_uses_demo_key_after_shop_name_change(self):
        call_command("seed_portfolio_data", stdout=StringIO())
        demo_shop = Shop.objects.get(demo_key="portfolio-demo")
        demo_shop_id = demo_shop.id
        demo_shop.name = "オーナーが変更した店舗名"
        demo_shop.save(update_fields=["name", "updated_at"])
        Shop.objects.create(name="〇〇食堂")

        call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        demo_shop.refresh_from_db()
        self.assertEqual(demo_shop.id, demo_shop_id)
        self.assertEqual(demo_shop.name, "〇〇食堂")
        self.assertEqual(Shop.objects.filter(demo_key="portfolio-demo").count(), 1)
        self.assertEqual(Shop.objects.filter(name="〇〇食堂").count(), 2)

    def test_reset_rolls_back_after_data_changes_when_late_seed_step_fails(self):
        call_command("seed_portfolio_data", stdout=StringIO())
        demo_shop = Shop.objects.get(demo_key="portfolio-demo")
        demo_shop.name = "変更中の店舗名"
        demo_shop.save(update_fields=["name", "updated_at"])
        extra_ingredient = Ingredient.objects.create(
            shop=demo_shop,
            name="rollbackで残る材料",
        )
        original_recipe = Recipe.objects.get(shop=demo_shop, name="カポナータ")
        original_recipe.description = "rollbackで残る説明"
        original_recipe.save(update_fields=["description", "updated_at"])

        def fail_after_reset_and_reseed(command, shop):
            shop.refresh_from_db()
            self.assertEqual(shop.name, "〇〇食堂")
            self.assertFalse(Ingredient.objects.filter(id=extra_ingredient.id).exists())
            self.assertEqual(Recipe.objects.filter(shop=shop).count(), 4)
            raise RuntimeError("simulated late demo seed failure")

        with patch(
            "api.management.commands.seed_portfolio_data.Command._seed_board_memos",
            autospec=True,
            side_effect=fail_after_reset_and_reseed,
        ):
            with self.assertRaisesMessage(
                RuntimeError,
                "simulated late demo seed failure",
            ):
                call_command("seed_portfolio_data", "--reset", stdout=StringIO())

        demo_shop.refresh_from_db()
        original_recipe.refresh_from_db()
        self.assertEqual(demo_shop.name, "変更中の店舗名")
        self.assertTrue(Ingredient.objects.filter(id=extra_ingredient.id).exists())
        self.assertEqual(original_recipe.description, "rollbackで残る説明")

    def test_demo_key_is_internal_and_normal_shops_allow_null(self):
        normal_shop = Shop.objects.create(name="通常店舗")
        self.assertIsNone(normal_shop.demo_key)
        call_command("seed_portfolio_data", stdout=StringIO())

        self.assertTrue(
            self.client.login(username="owner@example.com", password="password")
        )
        auth_response = self.client.get(reverse("auth_me"))
        shop_response = self.client.get(reverse("shop_me"))
        update_response = self.client.patch(
            reverse("shop_me"),
            '{"demo_key": "user-controlled"}',
            content_type="application/json",
        )

        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(shop_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertNotIn("demo_key", auth_response.data["shop"])
        self.assertNotIn("demo_key", shop_response.data)
        self.assertNotIn("demo_key", update_response.data)
        self.assertEqual(
            Shop.objects.get(demo_key="portfolio-demo").demo_key,
            "portfolio-demo",
        )

    def test_demo_key_is_unique_when_present(self):
        Shop.objects.create(name="デモ店舗", demo_key="portfolio-demo")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Shop.objects.create(name="重複デモ店舗", demo_key="portfolio-demo")
