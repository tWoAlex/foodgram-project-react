from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Prefetch
from django.db.transaction import atomic
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscription

from .filters import IngredientFilterSet, RecipeFilterSet
from .pagination import PageLimitPagination
from .permissions import IsActiveOrReadOnly, IsAuthorOrReadOnly
from .serializers import (AuthorSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)
from .utils import shopping_list

User = get_user_model()


class SubscriptionViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsActiveOrReadOnly,)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs['author_id'])
        subscriber = request.user
        subscribed = Subscription.objects.filter(
            subscriber=subscriber, author=author).exists()

        if author == subscriber:
            return Response('Нельзя подписаться на самого себя.',
                            status=status.HTTP_400_BAD_REQUEST)
        if subscribed:
            return Response('Вы уже подписаны на этого автора.',
                            status=status.HTTP_400_BAD_REQUEST)

        subscriber.subscribed.add(author)
        serializer = AuthorSerializer(author)
        serializer.context['request'] = self.request
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs['author_id'])
        subscriber = request.user
        subscribed = Subscription.objects.filter(
            subscriber=subscriber, author=author).exists()

        if not subscribed:
            return Response(
                'Вы не подписаны на данного автора.',
                status=status.HTTP_400_BAD_REQUEST)

        subscriber.subscribed.remove(author)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(DjoserUserViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    serializer_class = UserSerializer
    pagination_class = PageLimitPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            subscription = Subscription.objects.filter(
                author=OuterRef('pk'), subscriber=user)
            return User.objects.annotate(is_subscribed=Exists(subscription))
        return User.objects.all()

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

    @atomic
    def get_queryset(self):
        queryset = (
            Recipe.objects
            .prefetch_related('ingredients', 'ingredients__ingredient')
        )

        user = self.request.user
        if user.is_authenticated:
            favorites = FavoriteRecipe.objects.filter(
                recipe=OuterRef('pk'), user=user)
            shopping_cart = ShoppingCart.objects.filter(
                recipe=OuterRef('pk'), user=user)
            subscription = Subscription.objects.filter(
                author_id=OuterRef('id'), subscriber=user)
            return (
                queryset
                .annotate(is_favorited=Exists(favorites),
                          is_in_shopping_cart=Exists(shopping_cart))
                .prefetch_related(
                    Prefetch(
                        'author',
                        User.objects.annotate(
                            is_subscribed=Exists(subscription))
                    )
                )
            )
        return queryset.select_related('author')

    def __manage_list(self, request, obj_id,
                      serializer_class, linking_model=None):
        data = {'user': request.user.id, 'recipe': obj_id}
        link = serializer_class(data=data)

        if request.method == 'POST':
            link.is_valid(raise_exception=True)
            link.save()
            return Response(link.data, status=status.HTTP_201_CREATED)

        link_count, _ = linking_model.objects.filter(**data).delete()
        if link_count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Рецепт не в списке',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(IsActiveOrReadOnly,))
    def favorite(self, request, pk=None):
        return self.__manage_list(request, self.get_object().id,
                                  FavoriteRecipeSerializer, FavoriteRecipe)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(IsActiveOrReadOnly,))
    def shopping_cart(self, request, pk=None):
        return self.__manage_list(request, self.get_object().id,
                                  ShoppingCartSerializer, ShoppingCart)

    @action(methods=('GET',), detail=False,
            permission_classes=(permissions.IsAuthenticated,),)
    def download_shopping_cart(self, request):
        filename = 'Shopping cart.txt'

        purchases = shopping_list(request.user)
        return FileResponse(BytesIO(purchases.encode()),
                            filename=filename, as_attachment=True)
