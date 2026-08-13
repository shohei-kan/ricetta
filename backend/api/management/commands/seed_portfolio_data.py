from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
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


class Command(BaseCommand):
    help = "Seed portfolio/demo data for screenshots and public demo environments."
    demo_key = "portfolio-demo"

    def add_arguments(self, parser):
        parser.add_argument("--owner-email", default="owner@example.com")
        parser.add_argument("--staff-email", default="staff@example.com")
        parser.add_argument("--password", default="password")
        parser.add_argument("--shop-name", default="〇〇食堂")
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset only the fixed demo Shop data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        demo_shop = self._resolve_demo_shop(options["owner_email"])
        if options["reset"] and demo_shop is not None:
            self._reset_demo_shop(demo_shop)

        units = self._seed_units()
        owner = self._seed_user(
            email=options["owner_email"],
            password=options["password"],
            first_name="山田",
            last_name="太郎",
        )
        staff = self._seed_user(
            email=options["staff_email"],
            password=options["password"],
            first_name="佐藤",
            last_name="花子",
        )
        shop = self._seed_shop(
            options["shop_name"],
            demo_shop,
        )

        self._seed_membership(owner, shop, Membership.Role.OWNER, "山田 太郎")
        self._seed_membership(staff, shop, Membership.Role.STAFF, "佐藤 花子")

        categories = self._seed_categories(shop)
        ingredients = self._seed_ingredients(shop, units)
        recipes = self._seed_recipes(shop, owner, categories, units, ingredients)
        self._seed_prep_recipe_ingredients(shop, units, ingredients, recipes)
        recipes = self._seed_recipes(
            shop,
            owner,
            categories,
            units,
            ingredients,
            use_prep_recipe_ingredients=True,
        )
        self._seed_prep_tasks(shop, recipes, units)
        self._seed_board_memos(shop)

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded portfolio demo data. Accounts: "
                f"{options['owner_email']} / {options['password']}, "
                f"{options['staff_email']} / {options['password']}"
            )
        )

    def _resolve_demo_shop(self, owner_email):
        demo_shop = Shop.objects.filter(demo_key=self.demo_key).first()
        User = get_user_model()
        normalized_email = owner_email.strip().lower()
        owner = User.objects.filter(username=normalized_email).first()

        if demo_shop is not None:
            if owner is None:
                return demo_shop
            owner_membership = self._get_demo_owner_membership(owner)
            if owner_membership.shop != demo_shop:
                raise CommandError(
                    "Cannot use the portfolio demo Shop: demo_key and the known "
                    "demo owner's active owner Membership point to different Shops."
                )
            return demo_shop

        if owner is None:
            return None

        owner_membership = self._get_demo_owner_membership(owner)
        demo_shop = owner_membership.shop
        demo_shop.demo_key = self.demo_key
        demo_shop.save(update_fields=["demo_key", "updated_at"])
        return demo_shop

    def _get_demo_owner_membership(self, owner):
        memberships = list(
            Membership.objects.select_related("shop")
            .filter(user=owner)
            .order_by("id")
        )
        if len(memberships) != 1:
            raise CommandError(
                "Cannot identify the portfolio demo Shop: the known demo owner "
                f"has {len(memberships)} Membership candidates; expected exactly 1."
            )

        membership = memberships[0]
        if membership.role != Membership.Role.OWNER or not membership.is_active:
            raise CommandError(
                "Cannot identify the portfolio demo Shop: the known demo owner's "
                "only Membership must be active with role=owner."
            )
        return membership

    def _reset_demo_shop(self, demo_shop):

        # AWS公開デモの定期リセット用途。
        # reset対象は内部識別子で特定したデモShopに限定し、全Shop削除は絶対にしない。
        # 実データやデモ対象外Shopを巻き込まないため、User、Membership、Shopは維持する。
        # 削除対象: PrepTask, BoardMemo, RecipeStep, RecipeIngredient, Ingredient,
        # Recipe, Category, shop-specific Unit.
        PrepTask.objects.filter(shop=demo_shop).delete()
        BoardMemo.objects.filter(shop=demo_shop).delete()
        RecipeStep.objects.filter(recipe__shop=demo_shop).delete()
        RecipeIngredient.objects.filter(recipe__shop=demo_shop).delete()
        Ingredient.objects.filter(shop=demo_shop).delete()
        Recipe.objects.filter(shop=demo_shop).delete()
        Category.objects.filter(shop=demo_shop).delete()
        Unit.objects.filter(shop=demo_shop).delete()

    def _seed_units(self):
        unit_specs = [
            ("g", Unit.UnitType.WEIGHT, 1),
            ("kg", Unit.UnitType.WEIGHT, 2),
            ("ml", Unit.UnitType.VOLUME, 3),
            ("L", Unit.UnitType.VOLUME, 4),
            ("個", Unit.UnitType.COUNT, 5),
            ("本", Unit.UnitType.COUNT, 6),
            ("枚", Unit.UnitType.COUNT, 7),
            ("食分", Unit.UnitType.CUSTOM, 8),
            ("缶", Unit.UnitType.COUNT, 9),
            ("袋", Unit.UnitType.COUNT, 10),
            ("バッチ", Unit.UnitType.CUSTOM, 11),
        ]
        return {
            name: self._update_or_create_unit(name, unit_type, sort_order)
            for name, unit_type, sort_order in unit_specs
        }

    def _update_or_create_unit(self, name, unit_type, sort_order):
        unit = Unit.objects.filter(shop=None, name=name).order_by("id").first()
        if unit is None:
            return Unit.objects.create(
                shop=None,
                name=name,
                unit_type=unit_type,
                is_default=True,
                sort_order=sort_order,
                is_active=True,
            )
        unit.unit_type = unit_type
        unit.is_default = True
        unit.sort_order = sort_order
        unit.is_active = True
        unit.save()
        return unit

    def _seed_shop(self, shop_name, shop):
        if shop is None:
            shop = Shop(demo_key=self.demo_key)

        shop.name = shop_name
        shop.business_type = "小さな食堂・惣菜店"
        shop.memo = (
            "ポートフォリオ撮影・AWS公開デモ用のサンプル店舗です。"
            "本番運用データではありません。"
        )
        shop.save()
        return shop

    def _seed_user(self, email, password, first_name, last_name):
        User = get_user_model()
        normalized_email = email.strip().lower()
        user, created = User.objects.get_or_create(
            username=normalized_email,
            defaults={
                "email": normalized_email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )
        if not created:
            user.email = normalized_email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
        user.set_password(password)
        user.save()
        return user

    def _seed_membership(self, user, shop, role, display_name):
        primary = (
            Membership.objects.filter(user=user, is_active=True)
            .order_by("id")
            .first()
        )
        existing = Membership.objects.filter(user=user, shop=shop).order_by("id").first()

        if primary is None:
            membership = existing or Membership(user=user, shop=shop)
        elif primary.shop == shop:
            membership = primary
        elif existing is not None:
            primary.is_active = False
            primary.save()
            membership = existing
        else:
            primary.shop = shop
            membership = primary

        membership.role = role
        membership.display_name = display_name
        membership.is_active = True
        membership.save()

    def _seed_categories(self, shop):
        category_names = ["前菜", "ソース・仕込み", "惣菜", "デザート"]
        categories = {}
        for sort_order, name in enumerate(category_names, start=1):
            categories[name], _ = Category.objects.update_or_create(
                shop=shop,
                name=name,
                defaults={"sort_order": sort_order, "is_active": True},
            )
        return categories

    def _seed_ingredients(self, shop, units):
        specs = [
            {
                "name": "ホールトマト",
                "supplier": "中央青果",
                "memo": "トマトソースと煮込みに使う定番缶。",
                "cost_mode": Ingredient.CostMode.CONVERSION,
                "purchase_quantity": "1",
                "purchase_unit": units["缶"],
                "purchase_price": "180",
                "usage_unit": units["g"],
                "conversion_from_quantity": "1",
                "conversion_from_unit": units["缶"],
                "conversion_to_quantity": "400",
                "conversion_to_unit": units["g"],
            },
            {
                "name": "玉ねぎ",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "240",
                "usage_unit": units["g"],
            },
            {
                "name": "にんにく",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "100",
                "purchase_unit": units["g"],
                "purchase_price": "180",
                "usage_unit": units["g"],
            },
            {
                "name": "オリーブオイル",
                "supplier": "イタリア食材卸",
                "cost_mode": Ingredient.CostMode.CONVERSION,
                "purchase_quantity": "1",
                "purchase_unit": units["本"],
                "purchase_price": "1200",
                "usage_unit": units["ml"],
                "conversion_from_quantity": "1",
                "conversion_from_unit": units["本"],
                "conversion_to_quantity": "916",
                "conversion_to_unit": units["ml"],
            },
            {
                "name": "塩",
                "supplier": "業務用スーパー",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "120",
                "usage_unit": units["g"],
            },
            {
                "name": "きゅうり",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1",
                "purchase_unit": units["本"],
                "purchase_price": "70",
                "usage_unit": units["本"],
            },
            {
                "name": "にんじん",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "220",
                "usage_unit": units["g"],
            },
            {
                "name": "米酢",
                "supplier": "業務用スーパー",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["ml"],
                "purchase_price": "260",
                "usage_unit": units["ml"],
            },
            {
                "name": "グラニュー糖",
                "supplier": "業務用スーパー",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "260",
                "usage_unit": units["g"],
            },
            {
                "name": "なす",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "420",
                "usage_unit": units["g"],
            },
            {
                "name": "ズッキーニ",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "520",
                "usage_unit": units["g"],
            },
            {
                "name": "赤パプリカ",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "650",
                "usage_unit": units["g"],
            },
            {
                "name": "黄パプリカ",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "650",
                "usage_unit": units["g"],
            },
            {
                "name": "セロリ",
                "supplier": "中央青果",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["g"],
                "purchase_price": "360",
                "usage_unit": units["g"],
            },
            {
                "name": "ケーパー",
                "supplier": "イタリア食材卸",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "100",
                "purchase_unit": units["g"],
                "purchase_price": "320",
                "usage_unit": units["g"],
            },
            {
                "name": "白ワインビネガー",
                "supplier": "イタリア食材卸",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "500",
                "purchase_unit": units["ml"],
                "purchase_price": "520",
                "usage_unit": units["ml"],
            },
            {
                "name": "生クリーム",
                "supplier": "乳製品問屋",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["ml"],
                "purchase_price": "950",
                "usage_unit": units["ml"],
            },
            {
                "name": "牛乳",
                "supplier": "乳製品問屋",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1000",
                "purchase_unit": units["ml"],
                "purchase_price": "230",
                "usage_unit": units["ml"],
            },
            {
                "name": "卵黄",
                "supplier": "地元養鶏場",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1",
                "purchase_unit": units["個"],
                "purchase_price": "32",
                "usage_unit": units["個"],
            },
            {
                "name": "バニラビーンズ",
                "supplier": "製菓材料店",
                "cost_mode": Ingredient.CostMode.SAME_UNIT,
                "purchase_quantity": "1",
                "purchase_unit": units["本"],
                "purchase_price": "420",
                "usage_unit": units["本"],
            },
        ]

        ingredients = {}
        for spec in specs:
            name = spec.pop("name")
            ingredients[name] = self._update_or_create_ingredient(shop, name, spec)
        return ingredients

    def _update_or_create_ingredient(self, shop, name, defaults):
        ingredient = (
            Ingredient.objects.filter(shop=shop, name=name, is_active=True)
            .order_by("id")
            .first()
        )
        if ingredient is None:
            ingredient = Ingredient(shop=shop, name=name)
        if "ingredient_type" not in defaults:
            ingredient.ingredient_type = Ingredient.IngredientType.RAW
            ingredient.source_recipe = None
        for field, value in defaults.items():
            setattr(ingredient, field, value)
        ingredient.is_active = True
        ingredient.save()
        return ingredient

    def _seed_prep_recipe_ingredients(self, shop, units, ingredients, recipes):
        ingredients["トマトソース"] = self._update_or_create_ingredient(
            shop,
            "トマトソース",
            {
                "supplier": "",
                "memo": "仕込みレシピ「トマトソース」を別レシピの材料として使うための項目。",
                "ingredient_type": Ingredient.IngredientType.PREP_RECIPE,
                "source_recipe": recipes["トマトソース"],
                "cost_mode": Ingredient.CostMode.NONE,
                "purchase_quantity": None,
                "purchase_unit": None,
                "purchase_price": None,
                "usage_unit": units["g"],
                "conversion_from_quantity": None,
                "conversion_from_unit": None,
                "conversion_to_quantity": None,
                "conversion_to_unit": None,
            },
        )

    def _seed_recipes(
        self,
        shop,
        owner,
        categories,
        units,
        ingredients,
        use_prep_recipe_ingredients=False,
    ):
        recipes = {}
        caponata_tomato_ingredient = (
            ("トマトソース", "600", "g", "仕込み済みのトマトソースを使用", 7)
            if use_prep_recipe_ingredients
            else ("ホールトマト", "400", "g", "トマトソースでも可", 7)
        )
        recipe_specs = [
            {
                "name": "トマトソース",
                "category": categories["ソース・仕込み"],
                "description": "パスタ、煮込み、カポナータに回せる基本のトマトソース。",
                "recipe_type": Recipe.RecipeType.PREP,
                "base_yield_quantity": "2.5",
                "base_yield_unit": units["kg"],
                "selling_price": "0",
                "notes": "酸味が強い場合は煮詰め時間を少し長めにする。",
                "allergen_notes": "",
                "ingredients": [
                    ("ホールトマト", "1600", "g", "4缶分", 1),
                    ("玉ねぎ", "300", "g", "粗みじん", 2),
                    ("にんにく", "25", "g", "芯を取る", 3),
                    ("オリーブオイル", "80", "ml", "", 4),
                    ("塩", "12", "g", "仕上げで調整", 5),
                ],
                "steps": [
                    "鍋にオリーブオイルとにんにくを入れ、弱火で香りを出す。",
                    "玉ねぎを加えて透き通るまで炒める。",
                    "ホールトマトを加えて潰しながら20分煮る。",
                    "塩で味を整え、粗熱を取って保存容器へ移す。",
                ],
            },
            {
                "name": "ピクルス",
                "category": categories["前菜"],
                "description": "ランチの付け合わせや前菜盛りに使う彩りピクルス。",
                "recipe_type": Recipe.RecipeType.MENU,
                "base_yield_quantity": "10",
                "base_yield_unit": units["食分"],
                "selling_price": "540",
                "notes": "翌日以降が食べ頃。酸味を残すため煮立てすぎない。",
                "allergen_notes": "",
                "ingredients": [
                    ("きゅうり", "5", "本", "乱切り", 1),
                    ("にんじん", "300", "g", "拍子木切り", 2),
                    ("米酢", "500", "ml", "", 3),
                    ("グラニュー糖", "120", "g", "", 4),
                    ("塩", "18", "g", "", 5),
                ],
                "steps": [
                    "野菜を切り、清潔な保存容器に入れる。",
                    "米酢、砂糖、塩を鍋で温めて溶かす。",
                    "熱いピクルス液を野菜に注ぐ。",
                    "粗熱を取って冷蔵庫で一晩置く。",
                ],
            },
            {
                "name": "カポナータ",
                "category": categories["惣菜"],
                "description": "野菜をしっかり炒めて甘みを引き出す、定番の作り置き惣菜。",
                "recipe_type": Recipe.RecipeType.MENU,
                "base_yield_quantity": "8",
                "base_yield_unit": units["食分"],
                "selling_price": "600",
                "notes": (
                    "温製でも冷製でも提供でき、翌日の方が味がなじむ。"
                ),
                "allergen_notes": "特定原材料なし。提供時の添え物に注意。",
                "ingredients": [
                    ("なす", "600", "g", "大きめの角切り", 1),
                    ("ズッキーニ", "350", "g", "角切り", 2),
                    ("玉ねぎ", "300", "g", "1.5cm角", 3),
                    ("赤パプリカ", "220", "g", "角切り", 4),
                    ("黄パプリカ", "220", "g", "角切り", 5),
                    ("セロリ", "120", "g", "筋を取って薄切り", 6),
                    caponata_tomato_ingredient,
                    ("ケーパー", "24", "g", "軽く刻む", 8),
                    ("白ワインビネガー", "60", "ml", "", 9),
                    ("オリーブオイル", "140", "ml", "炒め用と仕上げ", 10),
                    ("グラニュー糖", "18", "g", "酸味調整", 11),
                    ("塩", "14", "g", "仕上げで調整", 12),
                ],
                "steps": [
                    "なすは塩少々を振って10分置き、水気を拭く。",
                    "大きめの鍋でオリーブオイルを温め、なすを焼き色がつくまで炒めて取り出す。",
                    "同じ鍋で玉ねぎ、セロリ、パプリカ、ズッキーニを順に炒める。",
                    "ホールトマト、ケーパー、白ワインビネガー、砂糖を加えて10分煮る。",
                    "なすを戻して全体を合わせ、塩で味を整える。",
                    "バットに広げて粗熱を取り、冷蔵庫で味をなじませる。",
                ],
            },
            {
                "name": "クレームブリュレ",
                "category": categories["デザート"],
                "description": "表面を香ばしく焼き上げる定番デザート。",
                "recipe_type": Recipe.RecipeType.MENU,
                "base_yield_quantity": "6",
                "base_yield_unit": units["個"],
                "selling_price": "620",
                "notes": "焼成後はしっかり冷やし、提供直前にキャラメリゼする。",
                "allergen_notes": "卵・乳",
                "ingredients": [
                    ("生クリーム", "600", "ml", "", 1),
                    ("牛乳", "200", "ml", "", 2),
                    ("卵黄", "8", "個", "", 3),
                    ("グラニュー糖", "120", "g", "生地用", 4),
                    ("バニラビーンズ", "1", "本", "", 5),
                ],
                "steps": [
                    "生クリーム、牛乳、バニラを温める。",
                    "卵黄と砂糖を混ぜ、温めた液体を少しずつ加える。",
                    "濾して器に流し、湯煎で焼く。",
                    "冷蔵庫で冷やし、提供前に砂糖を振って焼く。",
                ],
            },
        ]

        for spec in recipe_specs:
            recipes[spec["name"]] = self._update_or_create_recipe(
                shop=shop,
                owner=owner,
                units=units,
                ingredients=ingredients,
                spec=spec,
            )
        return recipes

    def _update_or_create_recipe(self, shop, owner, units, ingredients, spec):
        recipe = (
            Recipe.objects.filter(shop=shop, name=spec["name"], is_active=True)
            .order_by("id")
            .first()
        )
        if recipe is None:
            recipe = Recipe(shop=shop, name=spec["name"], created_by=owner)

        recipe.category = spec["category"]
        recipe.description = spec["description"]
        recipe.recipe_type = spec["recipe_type"]
        recipe.base_yield_quantity = Decimal(spec["base_yield_quantity"])
        recipe.base_yield_unit = spec["base_yield_unit"]
        recipe.selling_price = Decimal(spec["selling_price"])
        recipe.notes = spec["notes"]
        recipe.allergen_notes = spec["allergen_notes"]
        recipe.is_active = True
        recipe.updated_by = owner
        if recipe.created_by is None:
            recipe.created_by = owner
        recipe.save()

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredients[ingredient_name],
                    quantity=Decimal(quantity),
                    unit=units[unit_name],
                    memo=memo,
                    sort_order=sort_order,
                )
                for ingredient_name, quantity, unit_name, memo, sort_order in spec[
                    "ingredients"
                ]
            ]
        )

        RecipeStep.objects.filter(recipe=recipe).delete()
        RecipeStep.objects.bulk_create(
            [
                RecipeStep(
                    recipe=recipe,
                    step_number=index,
                    instruction=instruction,
                )
                for index, instruction in enumerate(spec["steps"], start=1)
            ]
        )
        return recipe

    def _seed_prep_tasks(self, shop, recipes, units):
        today = timezone.localdate()
        task_specs = [
            ("トマトソース", "2", "バッチ", PrepTask.Status.DOING, "トマトソースを仕込む", 1),
            ("ピクルス", "1", "バッチ", PrepTask.Status.TODO, "ピクルス液と野菜を準備", 2),
            ("カポナータ", "8", "食分", PrepTask.Status.TODO, "カポナータを仕込む", 3),
            ("クレームブリュレ", "8", "個", PrepTask.Status.DONE, "クレームブリュレを焼成", 4),
        ]
        for recipe_name, quantity, unit_name, status, memo, sort_order in task_specs:
            completed_at = timezone.now() if status == PrepTask.Status.DONE else None
            PrepTask.objects.update_or_create(
                shop=shop,
                date=today,
                recipe=recipes[recipe_name],
                defaults={
                    "planned_quantity": Decimal(quantity),
                    "planned_unit": units[unit_name],
                    "status": status,
                    "memo": memo,
                    "sort_order": sort_order,
                    "completed_at": completed_at,
                },
            )

    def _seed_board_memos(self, shop):
        memo_texts = ["玉ねぎ", "ラップ", "フライヤー油交換"]
        for text in memo_texts:
            memo = (
                BoardMemo.objects.filter(shop=shop, text=text)
                .order_by("id")
                .first()
            )
            if memo is None:
                BoardMemo.objects.create(shop=shop, text=text)
            else:
                field_names = {field.name for field in BoardMemo._meta.fields}
                update_fields = ["archived_at", "updated_at"]
                if "is_archived" in field_names:
                    setattr(memo, "is_archived", False)
                    update_fields.append("is_archived")
                if "archived_by" in field_names:
                    setattr(memo, "archived_by", None)
                    update_fields.append("archived_by")
                memo.archived_at = None
                memo.save(update_fields=update_fields)
