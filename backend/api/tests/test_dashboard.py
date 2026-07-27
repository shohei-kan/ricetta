# pyright: reportAttributeAccessIssue=false

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from api.models import Ingredient, PrepTask, Recipe, Unit

from .base import ApiTestCase


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
