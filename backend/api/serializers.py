import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Component, FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag)

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')

    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    def to_representation(self, instance):
        representative = super().to_representation(instance)
        representative.pop('password')
        return representative


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ComponentSerializer(IngredientSerializer):
    class Meta:
        model = Component
        fields = ('id', 'amount')
        read_only_fields = fields

    def to_representation(self, instance):
        data = IngredientSerializer().to_representation(
            instance.ingredient)
        data.update({'amount': instance.amount})
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image_str = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(image_str),
                               name='recipe.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'tags',
                  'image', 'cooking_time', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart')
        validators = (UniqueTogetherValidator(
            queryset=Recipe.objects.all(), fields=('author', 'name')),)

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = ComponentSerializer(many=True, read_only=True)
    image = Base64ImageField(required=True)

    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        data = super().to_internal_value(data)
        data['ingredients'] = ingredients
        return data

    def to_representation(self, instance):
        representative = super().to_representation(instance)
        representative['tags'] = TagSerializer(
            many=True).to_representation(instance.tags)
        return representative

    def run_validators(self, value):
        value['author'] = self.context['request'].user
        return super().run_validators(value)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        Component.objects.bulk_create(
            [Component(recipe=recipe,
                       ingredient_id=ingredient['id'],
                       amount=ingredient['amount'])
             for ingredient in ingredients])
        return recipe

    def __clear_components_and_tags__(self, instance):
        instance.ingredients.all().delete()

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance.ingredients.all().delete()
        instance.image.delete()

        instance.save(update_fields=validated_data)
        instance.tags.set(tags)
        Component.objects.bulk_create(
            [Component(recipe=instance,
                       ingredient_id=ingredient['id'],
                       amount=ingredient['amount'])
             for ingredient in ingredients])
        return super().update(instance, validated_data)


class RecipeInListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

    def to_representation(self, instance):
        return RecipeInListSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def to_representation(self, instance):
        return RecipeInListSerializer(instance.recipe).data


class AuthorSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes',)

    recipes = RecipeInListSerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['recipes_count'] = len(data['recipes'])
        return data
