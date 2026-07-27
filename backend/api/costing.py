from decimal import Decimal, InvalidOperation

from .models import Ingredient


def calculate_recipe_cost_summary(recipe):
    total_material_cost = Decimal("0")
    for recipe_ingredient in recipe.ingredients.select_related(
        "ingredient",
        "ingredient__usage_unit",
        "ingredient__purchase_unit",
        "ingredient__conversion_from_unit",
        "ingredient__conversion_to_unit",
        "unit",
    ):
        total_material_cost += _calculate_recipe_ingredient_cost(recipe_ingredient)

    material_cost = _calculate_unit_material_cost(
        total_material_cost,
        recipe.base_yield_quantity,
    )
    selling_price = recipe.selling_price
    gross_profit = None
    cost_rate = None
    if selling_price is not None:
        gross_profit = Decimal(selling_price) - material_cost
        if selling_price > 0:
            cost_rate = material_cost / Decimal(selling_price) * Decimal("100")

    return {
        "material_cost": _format_amount(material_cost),
        "selling_price": _format_amount(selling_price) if selling_price is not None else None,
        "cost_rate": _format_rate(cost_rate) if cost_rate is not None else None,
        "gross_profit": _format_amount(gross_profit) if gross_profit is not None else None,
    }


def _calculate_unit_material_cost(total_material_cost, base_yield_quantity):
    try:
        base_quantity = Decimal(base_yield_quantity)
        if base_quantity > 0:
            return Decimal(total_material_cost) / base_quantity
    except (InvalidOperation, TypeError, ZeroDivisionError):
        return Decimal(total_material_cost)
    return Decimal(total_material_cost)


def _calculate_recipe_ingredient_cost(recipe_ingredient):
    ingredient = recipe_ingredient.ingredient
    if ingredient.cost_mode == Ingredient.CostMode.NONE:
        return Decimal("0")
    if ingredient.usage_unit_id != recipe_ingredient.unit_id:
        return Decimal("0")

    try:
        if ingredient.cost_mode == Ingredient.CostMode.SAME_UNIT:
            if ingredient.purchase_price is None or not ingredient.purchase_quantity:
                return Decimal("0")
            unit_cost = Decimal(ingredient.purchase_price) / Decimal(
                ingredient.purchase_quantity
            )
            return unit_cost * Decimal(recipe_ingredient.quantity)

        if ingredient.cost_mode == Ingredient.CostMode.CONVERSION:
            required_values = [
                ingredient.purchase_price,
                ingredient.purchase_quantity,
                ingredient.conversion_from_quantity,
                ingredient.conversion_to_quantity,
            ]
            if any(value in (None, 0) for value in required_values):
                return Decimal("0")
            unit_cost = (
                Decimal(ingredient.purchase_price)
                * Decimal(ingredient.conversion_from_quantity)
                / Decimal(ingredient.purchase_quantity)
                / Decimal(ingredient.conversion_to_quantity)
            )
            return unit_cost * Decimal(recipe_ingredient.quantity)
    except (InvalidOperation, ZeroDivisionError):
        return Decimal("0")

    return Decimal("0")


def _format_amount(value):
    rounded = Decimal(value).quantize(Decimal("0.01"))
    return format(rounded.normalize(), "f")


def _format_rate(value):
    rounded = Decimal(value).quantize(Decimal("0.01"))
    return format(rounded, "f")
