from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from colorfield.fields import ColorField


User = get_user_model()


class Ingredient(models.Model):
    class MeasurementUnits(models.TextChoices):
        KG = 'кг', 'кг'
        G = 'г', 'г'
        NUM = 'шт', 'шт'
    name = models.CharField(max_length=50, unique=True,
                            verbose_name='Ингредиент')
    measurement_unit = models.CharField(choices=MeasurementUnits.choices,
                                        default=MeasurementUnits.NUM,
                                        max_length=3,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True,
                            verbose_name='Название')
    slug = models.SlugField(max_length=20, unique=True, verbose_name='Тэг')
    color = ColorField(default='#FFFFFF', unique=True, verbose_name='Цвет')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(max_length=1024, verbose_name='Описание')
    cooking_time = models.IntegerField(validators=(MinValueValidator(1),),
                                       verbose_name='Длительность')
    tags = models.ManyToManyField(to=Tag, through='TagRecipe',
                                  verbose_name='Тэги')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} от {self.author}'


class Component(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(to=Ingredient, on_delete=models.CASCADE,
                                   related_name='used_in',
                                   verbose_name='Ингредиент')
    amount = models.IntegerField(validators=(MinValueValidator(1),),
                                 verbose_name='Количество')

    class Meta:
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'

    def __str__(self):
        return (f'{self.recipe} → {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient}')


class TagRecipe(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    tag = models.ForeignKey(to=Tag, on_delete=models.CASCADE,
                            verbose_name='Тэг')

    class Meta:
        verbose_name = 'Связь рецепта и тэга'
        verbose_name_plural = 'Связи рецептов и тэгов'

    def __str__(self):
        return f'{self.recipe} → {self.tag}'
