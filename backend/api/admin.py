from django.contrib import admin

from .models import (
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


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    fields = ["name", "business_type", "memo"]
    list_display = ["id", "name", "business_type", "created_at", "updated_at"]
    search_fields = ["name", "business_type"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "shop", "role", "display_name", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["user__username", "user__email", "shop__name", "display_name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "shop", "name", "sort_order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "shop__name"]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["id", "shop", "name", "unit_type", "is_default", "sort_order", "is_active"]
    list_filter = ["unit_type", "is_default", "is_active"]
    search_fields = ["name", "shop__name"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "shop", "name", "supplier", "cost_mode", "is_active"]
    list_filter = ["cost_mode", "is_active"]
    search_fields = ["name", "supplier", "shop__name"]


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["id", "shop", "name", "category", "base_yield_quantity", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "shop__name", "category__name"]
    inlines = [RecipeIngredientInline, RecipeStepInline]


@admin.register(PrepTask)
class PrepTaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "shop",
        "date",
        "recipe",
        "planned_quantity",
        "planned_unit",
        "status",
        "sort_order",
        "completed_at",
    ]
    list_filter = ["status", "date"]
    search_fields = ["recipe__name", "shop__name", "memo"]


@admin.register(BoardMemo)
class BoardMemoAdmin(admin.ModelAdmin):
    list_display = ["id", "shop", "text", "archived_at", "created_at", "updated_at"]
    list_filter = ["archived_at"]
    search_fields = ["shop__name", "text"]
