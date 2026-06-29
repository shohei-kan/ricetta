from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from .models import Membership


def get_current_membership(user):
    if not user or not user.is_authenticated:
        raise NotAuthenticated("ログインが必要です。")

    membership = (
        Membership.objects.select_related("shop", "user")
        .filter(user=user, is_active=True)
        .order_by("id")
        .first()
    )
    if membership is None:
        raise PermissionDenied("有効な店舗所属がありません。")

    return membership


def get_current_shop(user):
    return get_current_membership(user).shop


def get_current_owner_membership(user):
    membership = get_current_membership(user)
    if membership.role != Membership.Role.OWNER:
        raise PermissionDenied("店舗情報を編集できるのはオーナーのみです。")
    return membership
