from django.contrib.auth import login, logout
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import action, api_view
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Ingredient, PrepTask, Recipe, Unit
from .serializers import (
    AuthMeSerializer,
    CategorySerializer,
    IngredientSerializer,
    LoginSerializer,
    PrepTaskSerializer,
    PrepTaskStatusSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    ShopSerializer,
    UnitSerializer,
)
from .shop_scope import get_current_membership, get_current_shop


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
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


class ShopMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = get_current_shop(request.user)
        return Response(ShopSerializer(shop).data)

    def patch(self, request):
        shop = get_current_shop(request.user)
        serializer = ShopSerializer(shop, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
        ).filter(shop=shop, date=target_date)
        prep_summary = {status_value: 0 for status_value, _label in PrepTask.Status.choices}
        for task in prep_tasks:
            prep_summary[task.status] += 1

        next_tasks = prep_tasks.exclude(status=PrepTask.Status.DONE).order_by(
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

    def _target_date(self, request):
        date_value = request.query_params.get("date")
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
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop)

    def perform_destroy(self, instance):
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
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop, is_default=False)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.shop_id is None:
            return Response(
                {"detail": "標準単位は編集できません。"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
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
            "purchase_unit",
            "usage_unit",
            "conversion_from_unit",
            "conversion_to_unit",
        ).filter(shop=shop, is_active=True)
        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def perform_create(self, serializer):
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop)

    def perform_destroy(self, instance):
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
                "ingredients__unit",
                "steps",
            )
            .filter(shop=shop, is_active=True)
        )
        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def perform_create(self, serializer):
        shop = get_current_shop(self.request.user)
        serializer.save(shop=shop, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
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

    def list(self, request, *args, **kwargs):
        target_date = self._target_date(request)
        if target_date is None:
            return Response(
                {"date": "YYYY-MM-DD形式で指定してください。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(date=target_date)
        serializer = self.get_serializer(queryset, many=True)
        summary = {status_value: 0 for status_value, _label in PrepTask.Status.choices}
        for task in queryset:
            summary[task.status] += 1

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
    def update_status(self, request, pk=None):
        task = self.get_object()
        serializer = PrepTaskStatusSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def _target_date(self, request):
        date_value = request.query_params.get("date")
        if not date_value:
            return timezone.localdate()
        return parse_date(date_value)
