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
        scope = "standard" if self.shop_id is None else self.shop.name
        return f"{self.name} ({scope})"
