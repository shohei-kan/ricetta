from datetime import date
from typing import Any, Optional, cast

from django.contrib.auth import login, logout
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import BoardMemo, Category, Ingredient, PrepTask, Recipe, Unit
from .serializers import (
    AuthMeSerializer,
    BoardMemoSerializer,
    CategorySerializer,
    IngredientSerializer,
    LoginSerializer,
    MembershipProfileSerializer,
    PrepTaskSerializer,
    PrepTaskStatusSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    ShopSerializer,
    UnitSerializer,
)
from .shop_scope import (
    get_current_membership,
    get_current_owner_membership,
    get_current_shop,
)


def get_query_param(request: Request, key: str) -> Optional[str]:
    value = request.query_params.get(key)
    return value if isinstance(value, str) else None


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)
        user = validated_data["user"]
        membership = get_current_membership(user)
        login(request, user)
        return Response(AuthMeSerializer(membership).data)


class CsrfView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"detail": "CSRF cookie set."})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "ログアウトしました。"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = get_current_membership(request.user)
        return Response(AuthMeSerializer(membership).data)

    def patch(self, request):
        membership = get_current_membership(request.user)
        serializer = MembershipProfileSerializer(
            membership,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AuthMeSerializer(membership).data)


class ShopMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = get_current_shop(request.user)
        return Response(ShopSerializer(shop).data)

    def patch(self, request):
        membership = get_current_owner_membership(request.user)
        shop = membership.shop
        serializer = ShopSerializer(shop, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        shop = get_current_shop(request.user)
        target_date = self._target_date(request)
        if target_date is None:
            return Response(
                {"date": "YYYY-MM-DD形式で指定してください。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prep_tasks = PrepTask.objects.select_related(
            "recipe",
            "planned_unit",
        ).filter(shop=shop).filter(active_prep_task_filter(target_date))
        prep_summary = {
            str(status_value): 0 for status_value, _label in PrepTask.Status.choices
        }
        for task in prep_tasks:
            prep_summary[str(task.status)] += 1

        next_tasks = prep_tasks.exclude(status=PrepTask.Status.DONE).order_by(
            prep_status_sort_order(),
            "sort_order",
            "id",
        )[:5]
        frequent_recipes = (
            Recipe.objects.select_related("category")
            .filter(shop=shop, is_active=True, prep_tasks__shop=shop)
            .annotate(prep_task_count=Count("prep_tasks"))
            .order_by("-prep_task_count", "name", "id")[:5]
        )

        return Response(
            {
                "date": target_date.isoformat(),
                "prep_summary": prep_summary,
                "next_tasks": [self._task_summary(task) for task in next_tasks],
                "frequent_recipes": [
                    self._recipe_summary(recipe) for recipe in frequent_recipes
                ],
                "stats": {
                    "recipe_count": Recipe.objects.filter(
                        shop=shop,
                        is_active=True,
                    ).count(),
                    "ingredient_count": Ingredient.objects.filter(
                        shop=shop,
                        is_active=True,
                    ).count(),
                    "prep_task_count": prep_tasks.count(),
                },
                "alerts": [],
            }
        )

    def _target_date(self, request: Request) -> Optional[date]:
        date_value = get_query_param(request, "date")
        if not date_value:
            return timezone.localdate()
        return parse_date(date_value)

    def _task_summary(self, task):
        return {
            "id": task.id,
            "recipe": {
                "id": task.recipe_id,
                "name": task.recipe.name,
            },
            "planned_quantity": task.planned_quantity,
            "planned_unit": {
                "id": task.planned_unit_id,
                "name": task.planned_unit.name,
            },
            "status": task.status,
            "memo": task.memo,
            "sort_order": task.sort_order,
        }

    def _recipe_summary(self, recipe):
        return {
            "id": recipe.id,
            "name": recipe.name,
            "category": {
                "id": recipe.category_id,
                "name": recipe.category.name,
            }
            if recipe.category_id
            else None,
        }


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        shop = get_current_shop(self.request.user)
        return Category.objects.filter(shop=shop, is_active=True)

    def perform_create(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "カテゴリを作成・編集できるのはオーナーのみです。",
        )
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "カテゴリを作成・編集できるのはオーナーのみです。",
        )
        serializer.save()

    def perform_destroy(self, instance):
        get_current_owner_membership(
            self.request.user,
            "カテゴリを作成・編集できるのはオーナーのみです。",
        )
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        shop = get_current_shop(self.request.user)
        return Unit.objects.filter(
            Q(shop__isnull=True) | Q(shop=shop),
            is_active=True,
        )

    def perform_create(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "単位を作成・編集できるのはオーナーのみです。",
        )
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop, is_default=False)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        get_current_owner_membership(
            request.user,
            "単位を作成・編集できるのはオーナーのみです。",
        )
        if instance.shop_id is None:
            return Response(
                {"detail": "標準単位は編集できません。"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        get_current_owner_membership(
            request.user,
            "単位を作成・編集できるのはオーナーのみです。",
        )
        if instance.shop_id is None:
            return Response(
                {"detail": "標準単位は削除できません。"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        shop = get_current_shop(self.request.user)
        queryset = Ingredient.objects.select_related(
            "source_recipe",
            "source_recipe__base_yield_unit",
            "purchase_unit",
            "usage_unit",
            "conversion_from_unit",
            "conversion_to_unit",
        ).filter(shop=shop, is_active=True)
        request = cast(Request, self.request)
        query = get_query_param(request, "q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def perform_create(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "材料を作成・編集できるのはオーナーのみです。",
        )
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "材料を作成・編集できるのはオーナーのみです。",
        )
        serializer.save()

    def perform_destroy(self, instance):
        get_current_owner_membership(
            self.request.user,
            "材料を作成・編集できるのはオーナーのみです。",
        )
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer
        return RecipeSerializer

    def get_queryset(self):
        shop = get_current_shop(self.request.user)
        queryset = (
            Recipe.objects.select_related(
                "category",
                "base_yield_unit",
                "created_by",
                "updated_by",
            )
            .prefetch_related(
                "ingredients__ingredient",
                "ingredients__ingredient__source_recipe",
                "ingredients__ingredient__source_recipe__base_yield_unit",
                "ingredients__unit",
                "steps",
            )
            .filter(shop=shop, is_active=True)
        )
        request = cast(Request, self.request)
        query = get_query_param(request, "q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        category_id = get_query_param(request, "category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def perform_create(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "レシピを作成・編集できるのはオーナーのみです。",
        )
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        get_current_owner_membership(
            self.request.user,
            "レシピを作成・編集できるのはオーナーのみです。",
        )
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        get_current_owner_membership(
            self.request.user,
            "レシピを作成・編集できるのはオーナーのみです。",
        )
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


class PrepTaskViewSet(viewsets.ModelViewSet):
    serializer_class = PrepTaskSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        shop = get_current_shop(self.request.user)
        return PrepTask.objects.select_related(
            "recipe",
            "planned_unit",
        ).filter(shop=shop).order_by("sort_order", "id")

    def list(self, request: Request, *args: Any, **kwargs: Any):
        target_date = self._target_date(request)
        if target_date is None:
            return Response(
                {"date": "YYYY-MM-DD形式で指定してください。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(active_prep_task_filter(target_date))
        serializer = self.get_serializer(queryset, many=True)
        summary = {
            str(status_value): 0 for status_value, _label in PrepTask.Status.choices
        }
        for task in queryset:
            summary[str(task.status)] += 1

        return Response(
            {
                "date": target_date.isoformat(),
                "summary": summary,
                "tasks": serializer.data,
            }
        )

    def perform_create(self, serializer):
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request: Request, pk: Any = None):
        task = self.get_object()
        serializer = PrepTaskStatusSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def _target_date(self, request: Request) -> Optional[date]:
        date_value = get_query_param(request, "date")
        if not date_value:
            return timezone.localdate()
        return parse_date(date_value)


class BoardMemoViewSet(viewsets.ModelViewSet):
    serializer_class = BoardMemoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        shop = get_current_shop(self.request.user)
        return BoardMemo.objects.filter(shop=shop)

    def list(self, request: Request, *args: Any, **kwargs: Any):
        queryset = self.get_queryset()
        if get_query_param(request, "include_archived") in {"1", "true"}:
            memos = list(queryset.order_by("-updated_at", "-id"))
        else:
            target_date = timezone.localdate()
            active_memos = list(
                queryset.filter(archived_at__isnull=True).order_by("created_at", "id")
            )
            archived_today_memos = list(
                queryset.filter(archived_at__date=target_date).order_by("-archived_at", "-id")
            )
            memos = active_memos + archived_today_memos

        return Response(self.get_serializer(memos, many=True).data)

    def perform_create(self, serializer):
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop)

    @action(detail=True, methods=["patch"])
    def archive(self, request, pk=None):
        memo = self.get_object()
        if memo.archived_at is None:
            memo.archived_at = timezone.now()
            memo.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(memo).data)

    @action(detail=True, methods=["patch"])
    def unarchive(self, request, pk=None):
        memo = self.get_object()
        if memo.archived_at is not None:
            memo.archived_at = None
            memo.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(memo).data)


def active_prep_task_filter(target_date):
    return Q(status__in=[PrepTask.Status.TODO, PrepTask.Status.DOING]) | Q(
        status=PrepTask.Status.DONE,
        completed_at__date=target_date,
    )


def prep_status_sort_order():
    return Case(
        When(status=PrepTask.Status.DOING, then=Value(0)),
        When(status=PrepTask.Status.TODO, then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )
