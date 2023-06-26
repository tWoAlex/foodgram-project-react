from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    message = 'Доступно только автору'

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_author = (obj.author == user
                     if user.is_authenticated
                     else False)
        return is_author or request.method in permissions.SAFE_METHODS


class IsActiveOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    message = 'Вы заблокированы'

    def __is_active(self, request):
        return (not request.user.is_blocked
                if request.user.is_authenticated
                else True)

    def has_permission(self, request, view):
        return self.__is_active(request) or request.method == 'GET'

    def has_object_permission(self, request, view, obj):
        return self.__is_active(request) or request.method == 'GET'
