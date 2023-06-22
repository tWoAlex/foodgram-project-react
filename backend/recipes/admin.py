from django.contrib import admin

from .models import (Component, FavoriteRecipe, Ingredient, Recipe,
                     ShoppingCart, Tag, TagRecipe)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name__icontains', 'tags__name',
                     'author__first_name', 'author__last_name')
    readonly_fields = ('favourited',)

    def favourited(self, obj):
        return obj.favorited_by.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
