from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Админ'
        USER = 'user', 'Пользователь'

    email = models.EmailField(unique=True, verbose_name='E-Mail')
    username = models.CharField(max_length=64, unique=True,
                                verbose_name='Логин',
                                validators=(UnicodeUsernameValidator(),))
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    role = models.CharField(choices=Roles.choices, default=Roles.USER,
                            max_length=5, verbose_name='Роль')
    subscribed = models.ManyToManyField(to='self', through='Subscription',
                                        symmetrical=False,)

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def __str__(self):
        if self.first_name:
            return f'{self.first_name} {self.last_name}'
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(to=User, on_delete=models.CASCADE,
                                   related_name='subscriptions',
                                   verbose_name='Подписчик')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='subscribers',
                               verbose_name='Подписан на')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (models.UniqueConstraint(fields=('subscriber', 'author'),
                                               name='unique_subscription'),)

    def __str__(self):
        return f'{self.subscriber} → {self.author}'
