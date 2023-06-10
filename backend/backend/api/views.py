from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (api_view, action,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, Tag,
                            FavouriteRecipe, ShoppingCart)

from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (TokenApproveSerializer, ChangePasswordSerializer,
                          UserSerializer, AuthorSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          FavouriteRecipeSerializer, ShoppingCartSerializer)
from .utils import create_token, delete_token


User = get_user_model()


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthorOrReadOnly,)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=FavouriteRecipeSerializer)
    def favourite(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': self.get_object().id}
        favourite = self.get_serializer(data=data)

        if request.method == 'POST':
            if favourite.is_valid():
                favourite.save()
                return Response(favourite.data, status=status.HTTP_201_CREATED)
            return Response(favourite.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        favourite = FavouriteRecipe.objects.filter(**data)
        if favourite.exists():
            favourite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Рецепт не в избранном',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=ShoppingCartSerializer)
    def shopping_cart(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': self.get_object().id}
        purchase = self.get_serializer(data=data)

        if request.method == 'POST':
            if purchase.is_valid():
                purchase.save()
                return Response(purchase.data, status=status.HTTP_201_CREATED)
            return Response(purchase.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        purchase = ShoppingCart.objects.filter(**data)
        if purchase.exists():
            purchase.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Рецепт не в корзине',
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    pagination_class = PageLimitPagination

    @action(methods=('GET',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('POST',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=ChangePasswordSerializer)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            request.user.set_password(serializer.data['new_password'])
            request.user.save()
            return Response('Пароль изменён', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


@api_view(http_method_names=('POST',))
def invoke_token(request):
    serializer = TokenApproveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.validated_data['email'],
                             password=serializer.validated_data['password'])

    delete_token(user)
    token = create_token(user)
    return Response({'auth_token': token.key}, status.HTTP_201_CREATED)


@api_view(http_method_names=('POST',))
@authentication_classes((TokenAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def revoke_token(request):
    delete_token(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)
