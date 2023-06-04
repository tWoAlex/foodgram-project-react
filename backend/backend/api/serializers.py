from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class TokenApproveSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

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
