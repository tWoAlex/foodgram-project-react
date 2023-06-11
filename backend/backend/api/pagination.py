from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class RecipePagination(PageLimitPagination):
    def __is_favourited__(self, request, queryset, param):
        is_favourited = int(param[0])
        if is_favourited:
            queryset = queryset.filter(favourited_by__user=request.user)
        return queryset

    def __is_in_shopping_cart__(self, request, queryset, param):
        is_in_shopping_cart = int(param[0])
        if is_in_shopping_cart:
            queryset = queryset.filter(in_shopping_cart__user=request.user)
        return queryset

    def __author__(self, request, queryset, param):
        author = int(param[0])
        return queryset.filter(author=author)

    def __tags__(self, request, queryset, param):
        for tag in param:
            queryset = queryset.filter(tags__slug=tag)
        return queryset

    def paginate_queryset(self, queryset, request, view=None):

        recipe_filters = (
            ('is_favourited', self.__is_favourited__),
            ('is_in_shopping_cart', self.__is_in_shopping_cart__),
            ('author', self.__author__),
            ('tags', self.__tags__)
        )

        params = dict(request.query_params)

        for param, queryset_filter_func in recipe_filters:
            if param in params:
                queryset = queryset_filter_func(
                    request, queryset, params[param])

        return super().paginate_queryset(queryset, request, view)
