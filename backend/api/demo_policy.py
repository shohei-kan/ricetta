from django.conf import settings
from rest_framework.exceptions import PermissionDenied


def deny_in_demo(message: str = "デモ環境では利用できません。") -> None:
    if getattr(settings, "DEMO_MODE", False):
        raise PermissionDenied(message)
