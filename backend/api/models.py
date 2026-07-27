from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Shop(TimeStampedModel):
    name = models.CharField(max_length=120)
    business_type = models.CharField(max_length=80, blank=True)
    memo = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Membership(TimeStampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        STAFF = "staff", "Staff"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
    )
    display_name = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "shop"],
                name="unique_membership_user_shop",
            )
        ]

    def __str__(self):
        return f"{self.user} / {self.shop} ({self.role})"


class Category(TimeStampedModel):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=80)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "name"],
                name="unique_category_shop_name",
            )
        ]

    def __str__(self):
        return self.name


class Unit(TimeStampedModel):
    class UnitType(models.TextChoices):
        WEIGHT = "weight", "Weight"
        VOLUME = "volume", "Volume"
        COUNT = "count", "Count"
        CUSTOM = "custom", "Custom"

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="units",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=40)
    unit_type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.CUSTOM,
    )
    is_default = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "name"],
                name="unique_unit_shop_name",
            )
        ]

    def __str__(self):
        shop = self.shop
        scope = "standard" if shop is None else shop.name
        return f"{self.name} ({scope})"


class Ingredient(TimeStampedModel):
    class IngredientType(models.TextChoices):
        RAW = "raw", "通常材料"
        PREP_RECIPE = "prep_recipe", "仕込みレシピ"

    class CostMode(models.TextChoices):
        NONE = "none", "原価計算しない"
        SAME_UNIT = "same_unit", "仕入単位のまま計算"
        CONVERSION = "conversion", "使用単位に換算して計算"

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    name = models.CharField(max_length=120)
    supplier = models.CharField(max_length=120, blank=True)
    memo = models.TextField(blank=True)
    ingredient_type = models.CharField(
        max_length=20,
        choices=IngredientType.choices,
        default=IngredientType.RAW,
    )
    source_recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.PROTECT,
        related_name="ingredient_links",
        blank=True,
        null=True,
    )
    cost_mode = models.CharField(
        max_length=20,
        choices=CostMode.choices,
        default=CostMode.NONE,
    )
    purchase_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    purchase_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="purchase_ingredients",
        blank=True,
        null=True,
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    usage_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="usage_ingredients",
        blank=True,
        null=True,
    )
    conversion_from_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    conversion_from_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="conversion_from_ingredients",
        blank=True,
        null=True,
    )
    conversion_to_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    conversion_to_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="conversion_to_ingredients",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "name"],
                condition=models.Q(is_active=True),
                name="unique_active_ingredient_shop_name",
            )
        ]

    def __str__(self):
        return self.name

    @property
    def unit_cost_label(self):
        unit_cost = self._unit_cost()
        usage_unit = self.usage_unit
        if unit_cost is None or usage_unit is None:
            return None
        return f"{self._format_decimal(unit_cost)}円 / {usage_unit.name}"

    def _unit_cost(self):
        try:
            if self.cost_mode == self.CostMode.SAME_UNIT:
                purchase_price = self.purchase_price
                purchase_quantity = self.purchase_quantity
                if (
                    purchase_price is None
                    or purchase_quantity is None
                    or purchase_quantity == 0
                ):
                    return None
                return purchase_price / purchase_quantity
            if self.cost_mode == self.CostMode.CONVERSION:
                purchase_price = self.purchase_price
                purchase_quantity = self.purchase_quantity
                conversion_from_quantity = self.conversion_from_quantity
                conversion_to_quantity = self.conversion_to_quantity
                if (
                    purchase_price is None
                    or purchase_quantity is None
                    or conversion_from_quantity is None
                    or conversion_to_quantity is None
                    or purchase_quantity == 0
                    or conversion_from_quantity == 0
                    or conversion_to_quantity == 0
                ):
                    return None
                return (
                    purchase_price
                    * conversion_from_quantity
                    / purchase_quantity
                    / conversion_to_quantity
                )
        except (InvalidOperation, ZeroDivisionError):
            return None
        return None

    def _format_decimal(self, value):
        rounded = value.quantize(Decimal("0.01"))
        return format(rounded.normalize(), "f")


class Recipe(TimeStampedModel):
    class RecipeType(models.TextChoices):
        PREP = "prep", "仕込み用"
        MENU = "menu", "販売商品"

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(max_length=120)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="recipes",
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)
    main_image = models.URLField(blank=True, null=True)
    recipe_type = models.CharField(
        max_length=20,
        choices=RecipeType.choices,
        default=RecipeType.PREP,
    )
    base_yield_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    base_yield_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="base_yield_recipes",
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True)
    allergen_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_recipes",
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_recipes",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "name"],
                condition=models.Q(is_active=True),
                name="unique_active_recipe_shop_name",
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="recipe_ingredients",
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="recipe_ingredients",
    )
    sort_order = models.PositiveIntegerField(default=0)
    memo = models.TextField(blank=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.recipe} / {self.ingredient}"


class RecipeStep(TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    step_number = models.PositiveIntegerField()
    instruction = models.TextField()
    image = models.URLField(blank=True, null=True)
    memo = models.TextField(blank=True)

    class Meta:
        ordering = ["step_number", "id"]

    def __str__(self):
        return f"{self.recipe} step {self.step_number}"


class PrepTask(TimeStampedModel):
    class Status(models.TextChoices):
        TODO = "todo", "未着手"
        DOING = "doing", "作業中"
        DONE = "done", "完了"

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="prep_tasks",
    )
    date = models.DateField()
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.PROTECT,
        related_name="prep_tasks",
    )
    planned_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    planned_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="prep_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    memo = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.date} / {self.recipe} ({self.status})"


class BoardMemo(TimeStampedModel):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="board_memos",
    )
    text = models.TextField()
    archived_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.text[:40]
