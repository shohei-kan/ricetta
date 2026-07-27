# pyright: reportAttributeAccessIssue=false

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import (
    Category,
    Ingredient,
    Membership,
    PrepTask,
    Recipe,
    Shop,
    Unit,
)


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

    def create_staff_membership(self):
        staff = self.create_user("staff@example.com", "password")
        membership = Membership.objects.create(
            user=staff,
            shop=self.shop,
            role=Membership.Role.STAFF,
            display_name="スタッフ",
        )
        return staff, membership

    def login_staff(self):
        self.create_staff_membership()
        logged_in = self.client.login(username="staff@example.com", password="password")
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
        ingredient_type=Ingredient.IngredientType.RAW,
        source_recipe=None,
    ):
        return Ingredient.objects.create(
            shop=shop or self.shop,
            name=name,
            ingredient_type=ingredient_type,
            source_recipe=source_recipe,
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
