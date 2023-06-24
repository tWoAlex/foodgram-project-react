from io import BytesIO

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (action, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Subscription
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from .filters import IngredientFilterSet, RecipeFilterSet
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly, IsActiveOrReadOnly
from .serializers import (AuthorSerializer, UserSerializer,
                          IngredientSerializer, TagSerializer,
                          RecipeSerializer,
                          FavoriteRecipeSerializer, ShoppingCartSerializer,)
from .utils import shopping_list


User = get_user_model()


@api_view(http_method_names=('POST', 'DELETE'))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsActiveOrReadOnly,))
def subscribe(request, pk=None):
    author = get_object_or_404(User, pk=pk)
    subscriber = request.user
    subscribed = Subscription.objects.filter(
        subscriber=subscriber, author=author).exists()

    if request.method == 'POST':
        if author == subscriber:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST)
        if subscribed:
            return Response(
                {'errors': 'Вы уже подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST)

        subscriber.subscribed.add(author)
        serializer = AuthorSerializer(author)
        serializer.context['request'] = request
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if not subscribed:
        return Response({'errors': 'Вы не подписаны на данного автора.'},
                        status=status.HTTP_400_BAD_REQUEST)
    subscriber.subscribed.remove(author)
    return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (TokenAuthentication,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination

    @action(methods=('GET',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthorOrReadOnly & IsActiveOrReadOnly,)

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(IsActiveOrReadOnly,),
            serializer_class=FavoriteRecipeSerializer)
    def favorite(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': self.get_object().id}
        favorite = self.get_serializer(data=data)

        if request.method == 'POST':
            if favorite.is_valid():
                favorite.save()
                print('saved')
                data = favorite.data
                print(data)
                return Response(favorite.data, status=status.HTTP_201_CREATED)
            return Response(favorite.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        favorite = FavoriteRecipe.objects.filter(**data)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Рецепт не в избранном',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(IsActiveOrReadOnly,),
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

    @action(methods=('GET',), detail=False,
            permission_classes=(permissions.IsAuthenticated,),)
    def download_shopping_cart(self, request):
        filename = 'Shopping cart.txt'

        purchases = shopping_list(request.user)
        return FileResponse(BytesIO(purchases.encode()),
                            filename=filename, as_attachment=True)
