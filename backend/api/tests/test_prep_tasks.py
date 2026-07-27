# pyright: reportAttributeAccessIssue=false

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from api.models import PrepTask, Recipe, Unit

from .base import ApiTestCase


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

    def test_staff_can_create_prep_task(self):
        self.login_staff()

        response = self.client.post(
            reverse("prep-task-list"),
            self.prep_task_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = PrepTask.objects.get(id=response.data["id"])
        self.assertEqual(task.shop, self.shop)
        self.assertEqual(task.status, PrepTask.Status.TODO)

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

    def test_staff_can_update_prep_task_status(self):
        self.login_staff()
        task = self.create_prep_task(status=PrepTask.Status.TODO)

        response = self.client.patch(
            reverse("prep-task-update-status", args=[task.id]),
            {"status": "doing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, PrepTask.Status.DOING)

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
