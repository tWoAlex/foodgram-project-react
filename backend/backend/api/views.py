from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, action,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response

from .pagination import PageLimitPagination
from .serializers import (TokenApproveSerializer,
                          UserSerializer, AuthorSerializer)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    pagination_class = PageLimitPagination

    @action(methods=('GET',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(permissions.IsAuthenticated,),)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('POST', 'DELETE'), detail=True,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=AuthorSerializer)
    def subscribe(self, request, pk=None):
        subscriber = request.user
        author = self.get_object()
        subscribed = author in subscriber.subscribed.all()

        if request.method == 'POST':
            if author == subscriber:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if subscribed:
                return Response(
                    {'errors': 'Уже подписан'},
                    status=status.HTTP_400_BAD_REQUEST)

            subscriber.subscribed.add(author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscribed:
            return Response({'errors': 'Не подписан на данного автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscriber.subscribed.remove(author)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=AuthorSerializer,
            pagination_class=PageLimitPagination)
    def subscriptions(self, request):
        subscriptions = request.user.subscribed.all()
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


def delete_token(user: User):
    Token.objects.filter(user=user).delete()


@api_view(http_method_names=('POST',))
def invoke_token(request):
    serializer = TokenApproveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.validated_data['email'],
                             password=serializer.validated_data['password'])

    delete_token(user)
    token = Token.objects.create(user=user)
    return Response({'auth_token': token.key}, status.HTTP_201_CREATED)


@api_view(http_method_names=('POST',))
@authentication_classes((TokenAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def revoke_token(request):
    delete_token(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)
