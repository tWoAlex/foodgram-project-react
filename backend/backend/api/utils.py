from rest_framework.authtoken.models import Token


def delete_token(user):
    Token.objects.filter(user=user).delete()


def create_token(user):
    return Token.objects.create(user=user)
