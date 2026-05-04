from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api.models import Category, Membership, Shop, Unit
from api.seed_data import DEFAULT_CATEGORIES, DEFAULT_UNITS


class Command(BaseCommand):
    help = "Seed Ricetta standard units and development shop data."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="owner@example.com")
        parser.add_argument("--password", default="password")
        parser.add_argument("--shop-name", default="〇〇食堂")
        parser.add_argument("--owner-name", default="山田 太郎")

    def handle(self, *args, **options):
        self._seed_standard_units()
        shop = self._seed_development_shop(options)
        user = self._seed_development_owner(options)
        self._seed_membership(user, shop, options["owner_name"])
        self._seed_categories(shop)

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded development data. This account is for local development only: "
                f"{options['email']} / {options['password']}"
            )
        )

    def _seed_standard_units(self):
        for sort_order, (name, unit_type) in enumerate(DEFAULT_UNITS, start=1):
            Unit.objects.update_or_create(
                shop=None,
                name=name,
                defaults={
                    "unit_type": unit_type,
                    "is_default": True,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

    def _seed_development_shop(self, options):
        shop, _ = Shop.objects.update_or_create(
            name=options["shop_name"],
            defaults={
                "business_type": "開発用",
                "memo": "seed_initial_data で作成した開発用Shopです。本番データではありません。",
            },
        )
        return shop

    def _seed_development_owner(self, options):
        User = get_user_model()
        email = options["email"].strip().lower()
        first_name, last_name = self._split_owner_name(options["owner_name"])
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )
        if not created:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
        user.set_password(options["password"])
        user.save()
        return user

    def _seed_membership(self, user, shop, display_name):
        Membership.objects.update_or_create(
            user=user,
            shop=shop,
            defaults={
                "role": Membership.Role.OWNER,
                "display_name": display_name,
                "is_active": True,
            },
        )

    def _seed_categories(self, shop):
        for sort_order, name in enumerate(DEFAULT_CATEGORIES, start=1):
            Category.objects.update_or_create(
                shop=shop,
                name=name,
                defaults={
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

    def _split_owner_name(self, owner_name):
        parts = owner_name.split(maxsplit=1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]
