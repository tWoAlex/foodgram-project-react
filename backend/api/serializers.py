import base64

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Component, FavouriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag, TagRecipe)

User = get_user_model()


class TokenApproveSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)

        email = data['email']
        password = data['password']
        user = get_object_or_404(User, email=email)

        if not user.check_password(password):
            raise serializers.ValidationError('Неверный пароль')
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True,
                                         validators=(validate_password,))

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный пароль')
        return value


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True,
                                     validators=(validate_password,))

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')

        user = self.context['request'].user
        data['is_subscribed'] = (
            instance in user.subscribed.all()
            if user.is_authenticated else False)
        return data


class AuthorSerializer(UserSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['recipes'] = []
        return data


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
        fields = '__all__'
        validators = (UniqueTogetherValidator(
            queryset=Recipe.objects.all(), fields=('author', 'name')),)

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = ComponentSerializer(many=True, read_only=True)
    image = Base64ImageField(required=True)

    def to_representation(self, instance):
        user = self.context['request'].user

        data = super().to_representation(instance)
        data['tags'] = TagSerializer(many=True).to_representation(
            instance.tags)
        data['ingredients'] = ComponentSerializer(
            many=True).to_representation(instance.ingredients)

        data['is_favourited'] = (
            FavouriteRecipe.objects.filter(user=user, recipe=instance).exists()
            if user.is_authenticated else False)
        data['is_in_shopping_cart'] = (
            ShoppingCart.objects.filter(user=user, recipe=instance).exists()
            if user.is_authenticated else False)
        return data

    def to_internal_value(self, data):
        tags = data.pop('tags')
        ingredients = data.pop('ingredients')

        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def run_validators(self, value):
        value['author'] = self.context['request'].user
        return super().run_validators(value)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag_id=tag, recipe=recipe)
        for ingredient in ingredients:
            Component.objects.create(recipe=recipe,
                                     ingredient_id=ingredient['id'],
                                     amount=ingredient['amount'])
        return recipe

    def __clear_components_and_tags__(self, instance):
        instance.tags.clear()
        instance.ingredients.all().delete()

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        self.__clear_components_and_tags__(instance)
        instance.image.delete()

        instance.save(update_fields=validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag_id=tag, recipe=instance)
        for ingredient in ingredients:
            Component.objects.create(recipe=instance,
                                     ingredient_id=ingredient['id'],
                                     amount=ingredient['amount'])
        return super().update(instance, validated_data)


class RecipeInListSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        recipe = instance.recipe
        return {'id': recipe.id, 'name': recipe.name,
                'cooking_time': recipe.cooking_time}


class FavouriteRecipeSerializer(RecipeInListSerializer):
    class Meta:
        model = FavouriteRecipe
        fields = '__all__'


class ShoppingCartSerializer(RecipeInListSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
