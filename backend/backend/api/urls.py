from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, invoke_token, revoke_token,
                    IngredientViewSet, RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', invoke_token),
    path('auth/token/logout/', revoke_token),
]
