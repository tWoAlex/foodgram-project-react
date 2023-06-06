from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from recipes.models import Component, Ingredient, Recipe, Tag


User = get_user_model()


class TokenApproveSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    class Meta:
        model = User

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

        data['is_subscribed'] = False
        user = self.context['request'].user
        if user.is_authenticated:
            data['is_subscribed'] = instance in user.subscribed.all()

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
    name = serializers.StringRelatedField(read_only=True,
                                          source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        read_only=True, source='ingredient.measurement_unit')
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = Component
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    # ingredients = ComponentSerializer(many=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(), many=True)

    # def validate(self, attrs):
    #     data = super().validate(attrs)
    #     data['author'] = self.context['request'].user
    #     return data

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        print('\n', validated_data, '\n')
        components = validated_data.pop('ingredients')
        print('\n', components, '\n')
        components = ComponentSerializer(
            many=True).to_internal_value(components)
        recipe = super().create(validated_data)
        components.update(recipe=recipe)
        return recipe

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagSerializer(many=True).to_representation(
            instance.tags)
        data['ingredients'] = ComponentSerializer(many=True).to_representation(
            instance.ingredients)
        return data
