from django_filters import rest_framework as filters


class RecipeFilterSet(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id',
                                  lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags__slug',
                              lookup_expr='exact')
