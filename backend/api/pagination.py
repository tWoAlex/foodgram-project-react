from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class RecipePagination(PageLimitPagination):
    def __is_favorited__(self, request, queryset, param):
        is_favorited = int(param[0])
        if is_favorited:
            return queryset.filter(favorited_by__user=request.user)
        return queryset

    def __is_in_shopping_cart__(self, request, queryset, param):
        is_in_shopping_cart = int(param[0])
        if is_in_shopping_cart:
            return queryset.filter(in_shopping_cart__user=request.user)
        return queryset

    def paginate_queryset(self, queryset, request, view=None):

        recipe_filters = (
            ('is_favorited', self.__is_favorited__),
            ('is_in_shopping_cart', self.__is_in_shopping_cart__),
        )

        params = dict(request.query_params)

        for param, queryset_filter_func in recipe_filters:
            if param in params:
                queryset = queryset_filter_func(
                    request, queryset, params[param])

        return super().paginate_queryset(queryset, request, view)
