from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    SubscriptionViewSet, UserViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(r'users/(?P<author_id>\d+)', SubscriptionViewSet, basename='subscribe')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
