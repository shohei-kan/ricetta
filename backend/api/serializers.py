from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Category, Membership, Shop, Unit
from .shop_scope import get_current_membership


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
