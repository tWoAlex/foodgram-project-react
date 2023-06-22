from io import BytesIO

from django.contrib.auth import get_user_model
from django.http import FileResponse
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (action, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from .filters import RecipeFilterSet
from .pagination import PageLimitPagination, RecipePagination
from .permissions import IsAuthorOrReadOnly, IsAuthenticatedAndActiveOrReadOnly
from .serializers import (AuthorSerializer, ChangePasswordSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, TokenApproveSerializer,
                          UserSerializer)
from .utils import shopping_list


User = get_user_model()


@api_view(http_method_names=('POST',))
def invoke_token(request):
    serializer = TokenApproveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if serializer.validated_data['user'].is_blocked:
        return Response('Вы заблокированы',
                        status=status.HTTP_401_UNAUTHORIZED)

    token = serializer.validated_data['user'].create_token()
    return Response({'auth_token': token.key}, status.HTTP_201_CREATED)


@api_view(http_method_names=('POST',))
@authentication_classes((TokenAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def revoke_token(request):
    request.user.delete_token()
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

    @action(methods=('POST',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(IsAuthenticatedAndActiveOrReadOnly,),
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
            permission_classes=(IsAuthenticatedAndActiveOrReadOnly,),
            serializer_class=AuthorSerializer)
    def subscribe(self, request, pk=None):
        subscriber = request.user
        author = self.get_object()
        subscribed = author in subscriber.subscribed.all()

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
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscribed:
            return Response({'errors': 'Вы не подписаны на данного автора.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscriber.subscribed.remove(author)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False,
            authentication_classes=(TokenAuthentication,),
            permission_classes=(IsAuthenticatedAndActiveOrReadOnly,),
            serializer_class=AuthorSerializer,
            pagination_class=PageLimitPagination)
    def subscriptions(self, request):
        subscriptions = request.user.subscribed.all()
        page = self.paginate_queryset(subscriptions)

        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthorOrReadOnly,)

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=(IsAuthenticatedAndActiveOrReadOnly,),
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
            permission_classes=(IsAuthenticatedAndActiveOrReadOnly,),
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
            permission_classes=(IsAuthenticatedAndActiveOrReadOnly,),)
    def download_shopping_cart(self, request):
        filename = 'Shopping cart.txt'

        purchases = shopping_list(request.user)
        return FileResponse(BytesIO(purchases.encode()),
                            filename=filename, as_attachment=True)
