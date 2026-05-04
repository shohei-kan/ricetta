from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .costing import calculate_recipe_cost_summary
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
from .shop_scope import get_current_membership, get_current_shop


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if user is None:
            raise serializers.ValidationError(
                {"detail": "メールアドレスまたはパスワードが正しくありません。"}
            )
        if not user.is_active:
            raise serializers.ValidationError({"detail": "このユーザーは無効です。"})

        attrs["user"] = user
        return attrs


class UserSummarySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name"]

    def get_name(self, obj):
        full_name = obj.get_full_name()
        return full_name or obj.username


class ShopSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name"]


class MembershipSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["role"]


class AuthMeSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSummarySerializer(obj.user).data

    def get_shop(self, obj):
        return ShopSummarySerializer(obj.shop).data

    def get_membership(self, obj):
        return MembershipSummarySerializer(obj).data


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", "business_type", "memo", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "sort_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CategorySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class UnitSerializer(serializers.ModelSerializer):
    is_standard = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "id",
            "name",
            "unit_type",
            "is_default",
            "sort_order",
            "is_active",
            "is_standard",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_default", "is_standard", "created_at", "updated_at"]

    def get_is_standard(self, obj):
        return obj.shop_id is None

    def validate(self, attrs):
        request = self.context.get("request")
        if request is not None:
            get_current_membership(request.user)
        return attrs


class UnitSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name"]


class IngredientSerializer(serializers.ModelSerializer):
    purchase_unit = UnitSummarySerializer(read_only=True)
    usage_unit = UnitSummarySerializer(read_only=True)
    conversion_from_unit = UnitSummarySerializer(read_only=True)
    conversion_to_unit = UnitSummarySerializer(read_only=True)
    purchase_unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.none(),
        source="purchase_unit",
        required=False,
        allow_null=True,
        write_only=True,
    )
    usage_unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.none(),
        source="usage_unit",
        required=False,
        allow_null=True,
        write_only=True,
    )
    conversion_from_unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.none(),
        source="conversion_from_unit",
        required=False,
        allow_null=True,
        write_only=True,
    )
    conversion_to_unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.none(),
        source="conversion_to_unit",
        required=False,
        allow_null=True,
        write_only=True,
    )
    conversion = serializers.SerializerMethodField()
    unit_cost_label = serializers.CharField(read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "supplier",
            "memo",
            "cost_mode",
            "purchase_quantity",
            "purchase_unit",
            "purchase_unit_id",
            "purchase_price",
            "usage_unit",
            "usage_unit_id",
            "conversion",
            "conversion_from_quantity",
            "conversion_from_unit",
            "conversion_from_unit_id",
            "conversion_to_quantity",
            "conversion_to_unit",
            "conversion_to_unit_id",
            "unit_cost_label",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "purchase_unit",
            "usage_unit",
            "conversion",
            "conversion_from_unit",
            "conversion_to_unit",
            "unit_cost_label",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is None:
            return
        shop = get_current_shop(request.user)
        scoped_units = Unit.objects.filter(
            Q(shop__isnull=True) | Q(shop=shop),
            is_active=True,
        )
        for field_name in [
            "purchase_unit_id",
            "usage_unit_id",
            "conversion_from_unit_id",
            "conversion_to_unit_id",
        ]:
            self.fields[field_name].queryset = scoped_units

    def get_conversion(self, obj):
        if obj.cost_mode != Ingredient.CostMode.CONVERSION:
            return None
        return {
            "from_quantity": obj.conversion_from_quantity,
            "from_unit": UnitSummarySerializer(obj.conversion_from_unit).data
            if obj.conversion_from_unit_id
            else None,
            "to_quantity": obj.conversion_to_quantity,
            "to_unit": UnitSummarySerializer(obj.conversion_to_unit).data
            if obj.conversion_to_unit_id
            else None,
        }

    def validate(self, attrs):
        values = self._merged_values(attrs)
        cost_mode = values.get("cost_mode") or Ingredient.CostMode.NONE

        if cost_mode == Ingredient.CostMode.NONE:
            return attrs
        if cost_mode == Ingredient.CostMode.SAME_UNIT:
            self._validate_same_unit(values)
            return attrs
        if cost_mode == Ingredient.CostMode.CONVERSION:
            self._validate_conversion(values)
            return attrs

        raise serializers.ValidationError({"cost_mode": "不正な原価計算モードです。"})

    def _merged_values(self, attrs):
        fields = [
            "cost_mode",
            "purchase_quantity",
            "purchase_unit",
            "purchase_price",
            "usage_unit",
            "conversion_from_quantity",
            "conversion_from_unit",
            "conversion_to_quantity",
            "conversion_to_unit",
        ]
        values = {}
        for field in fields:
            if field in attrs:
                values[field] = attrs[field]
            elif self.instance is not None:
                values[field] = getattr(self.instance, field)
            else:
                values[field] = None
        return values

    def _validate_same_unit(self, values):
        self._require_fields(
            values,
            ["purchase_quantity", "purchase_unit", "purchase_price", "usage_unit"],
        )
        self._validate_positive(values, "purchase_quantity")
        self._validate_non_negative(values, "purchase_price")
        if values["purchase_unit"] != values["usage_unit"]:
            raise serializers.ValidationError(
                {"usage_unit_id": "same_unitでは使用単位を仕入単位と同じにしてください。"}
            )

    def _validate_conversion(self, values):
        self._require_fields(
            values,
            [
                "purchase_quantity",
                "purchase_unit",
                "purchase_price",
                "usage_unit",
                "conversion_from_quantity",
                "conversion_from_unit",
                "conversion_to_quantity",
                "conversion_to_unit",
            ],
        )
        self._validate_positive(values, "purchase_quantity")
        self._validate_non_negative(values, "purchase_price")
        self._validate_positive(values, "conversion_from_quantity")
        self._validate_positive(values, "conversion_to_quantity")
        if values["conversion_from_unit"] != values["purchase_unit"]:
            raise serializers.ValidationError(
                {"conversion_from_unit_id": "換算元単位は仕入単位と同じにしてください。"}
            )
        if values["conversion_to_unit"] != values["usage_unit"]:
            raise serializers.ValidationError(
                {"conversion_to_unit_id": "換算先単位は使用単位と同じにしてください。"}
            )

    def _require_fields(self, values, fields):
        errors = {}
        for field in fields:
            if values.get(field) is None:
                errors[self._input_field_name(field)] = "この項目は必須です。"
        if errors:
            raise serializers.ValidationError(errors)

    def _validate_positive(self, values, field):
        value = values.get(field)
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                {self._input_field_name(field): "0より大きい値を入力してください。"}
            )

    def _validate_non_negative(self, values, field):
        value = values.get(field)
        if value is not None and value < 0:
            raise serializers.ValidationError(
                {self._input_field_name(field): "0以上の値を入力してください。"}
            )

    def _input_field_name(self, field):
        unit_fields = {
            "purchase_unit": "purchase_unit_id",
            "usage_unit": "usage_unit_id",
            "conversion_from_unit": "conversion_from_unit_id",
            "conversion_to_unit": "conversion_to_unit_id",
        }
        return unit_fields.get(field, field)


class ScopedUnitField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request")
        if request is None:
            return Unit.objects.none()
        shop = get_current_shop(request.user)
        return Unit.objects.filter(
            Q(shop__isnull=True) | Q(shop=shop),
            is_active=True,
        )


class ScopedCategoryField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request")
        if request is None:
            return Category.objects.none()
        shop = get_current_shop(request.user)
        return Category.objects.filter(shop=shop, is_active=True)


class ScopedIngredientField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request")
        if request is None:
            return Ingredient.objects.none()
        shop = get_current_shop(request.user)
        return Ingredient.objects.filter(shop=shop, is_active=True)


class ScopedRecipeField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request")
        if request is None:
            return Recipe.objects.none()
        shop = get_current_shop(request.user)
        return Recipe.objects.filter(shop=shop, is_active=True)


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    ingredient_id = ScopedIngredientField(source="ingredient")
    unit_id = ScopedUnitField(source="unit")

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_id", "quantity", "unit_id", "sort_order", "memo"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("0より大きい値を入力してください。")
        return value

    def validate(self, attrs):
        ingredient = attrs.get("ingredient")
        unit = attrs.get("unit")
        if (
            ingredient is not None
            and unit is not None
            and ingredient.cost_mode != Ingredient.CostMode.NONE
            and ingredient.usage_unit_id != unit.id
        ):
            raise serializers.ValidationError(
                {"unit_id": "原価計算する材料では使用単位と同じ単位を指定してください。"}
            )
        return attrs


class RecipeStepWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeStep
        fields = ["step_number", "instruction", "image", "memo"]

    def validate_step_number(self, value):
        if value < 1:
            raise serializers.ValidationError("1以上の値を入力してください。")
        return value


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()
    unit = UnitSummarySerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "quantity", "unit", "sort_order", "memo"]

    def get_ingredient(self, obj):
        return {"id": obj.ingredient_id, "name": obj.ingredient.name}


class RecipeStepReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeStep
        fields = ["id", "step_number", "instruction", "image", "memo"]


class RecipeListSerializer(serializers.ModelSerializer):
    category = CategorySummarySerializer(read_only=True)
    base_yield_unit = UnitSummarySerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "category",
            "base_yield_quantity",
            "base_yield_unit",
            "main_image",
            "updated_at",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    category = CategorySummarySerializer(read_only=True)
    category_id = ScopedCategoryField(
        source="category",
        required=False,
        allow_null=True,
        write_only=True,
    )
    base_yield_unit = UnitSummarySerializer(read_only=True)
    base_yield_unit_id = ScopedUnitField(source="base_yield_unit", write_only=True)
    ingredients = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    cost_summary = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "category",
            "category_id",
            "description",
            "main_image",
            "base_yield_quantity",
            "base_yield_unit",
            "base_yield_unit_id",
            "selling_price",
            "notes",
            "allergen_notes",
            "ingredients",
            "steps",
            "cost_summary",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "category",
            "base_yield_unit",
            "ingredients",
            "steps",
            "cost_summary",
            "created_at",
            "updated_at",
        ]

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        if "ingredients" in data:
            serializer = RecipeIngredientWriteSerializer(
                data=data.get("ingredients"),
                many=True,
                context=self.context,
            )
            if not serializer.is_valid():
                raise serializers.ValidationError({"ingredients": serializer.errors})
            internal["ingredients"] = serializer.validated_data
        if "steps" in data:
            serializer = RecipeStepWriteSerializer(
                data=data.get("steps"),
                many=True,
                context=self.context,
            )
            if not serializer.is_valid():
                raise serializers.ValidationError({"steps": serializer.errors})
            internal["steps"] = serializer.validated_data
        return internal

    def get_ingredients(self, obj):
        return RecipeIngredientReadSerializer(obj.ingredients.all(), many=True).data

    def get_steps(self, obj):
        return RecipeStepReadSerializer(obj.steps.all(), many=True).data

    def get_cost_summary(self, obj):
        return calculate_recipe_cost_summary(obj)

    def validate_base_yield_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("0より大きい値を入力してください。")
        return value

    def validate_selling_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("0以上の値を入力してください。")
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients", [])
        steps_data = validated_data.pop("steps", [])
        recipe = Recipe.objects.create(**validated_data)
        self._replace_ingredients(recipe, ingredients_data)
        self._replace_steps(recipe, steps_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        steps_data = validated_data.pop("steps", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            self._replace_ingredients(instance, ingredients_data)
        if steps_data is not None:
            instance.steps.all().delete()
            self._replace_steps(instance, steps_data)
        return instance

    def _replace_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)

    def _replace_steps(self, recipe, steps_data):
        for step_data in steps_data:
            RecipeStep.objects.create(recipe=recipe, **step_data)


class RecipeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name"]


class PrepTaskSerializer(serializers.ModelSerializer):
    recipe = RecipeSummarySerializer(read_only=True)
    recipe_id = ScopedRecipeField(source="recipe", write_only=True)
    planned_unit = UnitSummarySerializer(read_only=True)
    planned_unit_id = ScopedUnitField(source="planned_unit", write_only=True)

    class Meta:
        model = PrepTask
        fields = [
            "id",
            "date",
            "recipe",
            "recipe_id",
            "planned_quantity",
            "planned_unit",
            "planned_unit_id",
            "status",
            "memo",
            "sort_order",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recipe",
            "planned_unit",
            "completed_at",
            "created_at",
            "updated_at",
        ]

    def validate_planned_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("0より大きい値を入力してください。")
        return value

    def create(self, validated_data):
        self._set_completed_at(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._set_completed_at(validated_data, instance=instance)
        return super().update(instance, validated_data)

    def _set_completed_at(self, attrs, instance=None):
        status = attrs.get("status")
        if status is None and instance is None:
            status = PrepTask.Status.TODO
        elif status is None:
            return

        if status == PrepTask.Status.DONE:
            if instance is None or instance.status != PrepTask.Status.DONE or not instance.completed_at:
                attrs["completed_at"] = timezone.now()
        else:
            attrs["completed_at"] = None


class PrepTaskStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=PrepTask.Status.choices)

    class Meta:
        model = PrepTask
        fields = ["id", "status", "completed_at"]
        read_only_fields = ["id", "completed_at"]

    def update(self, instance, validated_data):
        status = validated_data["status"]
        instance.status = status
        instance.completed_at = timezone.now() if status == PrepTask.Status.DONE else None
        instance.save(update_fields=["status", "completed_at", "updated_at"])
        return instance
