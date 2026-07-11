from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("board-memos", views.BoardMemoViewSet, basename="board-memo")
router.register("categories", views.CategoryViewSet, basename="category")
router.register("ingredients", views.IngredientViewSet, basename="ingredient")
router.register("prep-tasks", views.PrepTaskViewSet, basename="prep-task")
router.register("recipes", views.RecipeViewSet, basename="recipe")
router.register("units", views.UnitViewSet, basename="unit")

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path("auth/csrf/", views.CsrfView.as_view(), name="auth_csrf"),
    path("auth/login/", views.LoginView.as_view(), name="auth_login"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth_logout"),
    path("auth/me/", views.MeView.as_view(), name="auth_me"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("shop/me/", views.ShopMeView.as_view(), name="shop_me"),
    path("", include(router.urls)),
]
