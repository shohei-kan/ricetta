from django.contrib import admin

from .models import Category, Ingredient, Membership, Shop, Unit


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
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
