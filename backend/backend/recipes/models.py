from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from colorfield.fields import ColorField

User = get_user_model()


class Ingredient(models.Model):
    class MeasurementUnits(models.TextChoices):
        KG = 'kg', 'кг'
        G = 'g', 'г'
        NUM = 'pcs', 'шт'
    name = models.CharField(max_length=50, unique=True,
                            verbose_name='Ингредиент')
    maesurement_unit = models.CharField(choices=MeasurementUnits.choices,
                                        default=MeasurementUnits.NUM,
                                        max_length=3,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=100, verbose_name='Рецепт')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    tags = models.ManyToManyField(to=Tag, through='TagRecipe',
                                  verbose_name='Тэги')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(to=Ingredient, on_delete=models.CASCADE,
                                   related_name='used_in',
                                   verbose_name='Ингредиент')
    amount = models.IntegerField(blank=False, null=False,
                                 validators=(MinValueValidator(1),),
                                 verbose_name='Количество')

    class Meta:
        verbose_name = 'Порция ингредиента'
        verbose_name_plural = 'Порции ингредиентов'

    def __str__(self):
        return (f'{self.amount} {self.ingredient.maesurement_unit}'
                f' {self.ingredient}')


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
