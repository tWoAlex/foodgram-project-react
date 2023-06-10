from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    message = 'Only author allowed'

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_author = (obj.author == user
                     if user.is_authenticated
                     else False)

        return is_author or request.method == 'GET'
