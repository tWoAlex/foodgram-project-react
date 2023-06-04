from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, invoke_token, revoke_token

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', invoke_token),
    path('auth/token/logout/', revoke_token),
]
