from django_filters import rest_framework as filters


class FavoriteFilter(filters.BooleanFilter):
    def filter(self, qs, value):
        user = self.extra.get('user')
        if user and value:
            return qs.filter(favorited_by__user=user)
        return qs


class ShoppingCartFilter(filters.BooleanFilter):
    def filter(self, qs, value):
        user = self.extra.get('user')
        if user and value:
            return qs.filter(in_shopping_cart__user=user)
        return qs


class RecipeFilterSet(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id',
                                  lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags__slug',
                              lookup_expr='exact')
    is_favorited = FavoriteFilter()
    is_in_shopping_cart = ShoppingCartFilter()

    def filter_queryset(self, queryset):
        user = self.request.user
        if user.is_authenticated:
            self.filters['is_favorited'].extra['user'] = user
            self.filters['is_in_shopping_cart'].extra['user'] = user
        return super().filter_queryset(queryset)


class IngredientFilterSet(filters.FilterSet):
    name = filters.CharFilter(field_name='name',
                              lookup_expr='icontains')
